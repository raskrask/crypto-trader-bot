from datetime import datetime, timedelta
import pandas as pd
from utils.s3_helper import get_s3_helper
from models.binance_fetcher import BinanceFetcher
from dateutil.relativedelta import relativedelta
from config.settings import settings
from utils.date_helper import get_days_ago
from config.config_manager import get_config_manager


class CryptoTrainingDataset:

    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.markets= ['VITE/USDT', 'BTC/USDT']
        self.interval_min = 15  # 足の間隔を秒単位で指定。この場合は15分足

        self.created_at: datetime = datetime.utcnow()
        self.end_date: datetime = self.created_at.date() - timedelta(days=1)
        self.start_date: datetime = self.end_date - relativedelta(
            months=self.config_data.get("training_period_months", 3)
        )
        self.data: pd.DataFrame = pd.DataFrame()
        self.fetcher = BinanceFetcher()
        self.s3 = get_s3_helper()

    def get_data(self):
        """ 教師データをロード or 収集 & 統合 """
        self.data = self.load()

        if self.data is None or self.data.empty:
            for symbol in self.markets:
                collected_data = pd.DataFrame()
                current_date = self.start_date
                while current_date < self.end_date:
                    df_ohlcv = self.fetch_ohlcv( symbol, current_date )
                    collected_data = pd.concat([collected_data, df_ohlcv], ignore_index=True)
                    current_date += timedelta(days=1)
                self.aggregate(symbol, collected_data)
            self.save()

        return self.data

    def fetch_ohlcv(self, symbol, date):
        file_key = self.historical_data_path(symbol, self.interval_min, date)
        df = self.s3.load_parquet_from_s3(file_key)
        if df.empty:
            df = self.fetcher.fetch_daily_ohlcv(symbol, self.interval_min, get_days_ago(date))
            self.s3.save_parquet_to_s3(df, file_key)
        return df

    def aggregate(self, symbol: str, additional_data: pd.DataFrame):
        """ 既存のデータに追加のデータを統合 """
        symbol = symbol.replace('/','_')
        column_mapping = {v: f"{v}_{symbol}" for v in additional_data.columns if v != "timestamp"}
        additional_data = additional_data.rename(columns=column_mapping)
        if self.data is None or self.data.empty:
            self.data = additional_data
        else:
            self.data = pd.merge(self.data, additional_data, on="timestamp")
            merged_df = pd.merge(self.data, additional_data, on="timestamp", how="outer", indicator=True)
        return self.data

    def load(self):
        """ S3 から教師データをロード """
        s3_path = f"training_datasets/{self.start_date}_{self.end_date}.parquet"
        self.data = self.s3.load_parquet_from_s3(s3_path)
        #self.data = pd.DataFrame()
        return self.data

    def save(self):
        """ 教師データを S3 に保存 """
        if self.data is not None and not self.data.empty:
            s3_path = f"training_datasets/{self.start_date}_{self.end_date}.parquet"
            self.s3.save_parquet_to_s3(self.data, s3_path)

    @staticmethod
    def historical_data_path(symbol: str, timeframe: str, date: str):
        """
        過去データの S3 ファイルパスを生成
        s3_folder/BTC_USDT/daily_15m/BTC_USDT_daily_15m_2025-02-10.parquet
        :param symbol: マーケット通貨ペア（例: "BTC_USDT"）
        :param timeframe: 時間軸
        :param date: "YYYY-MM-DD" の形式の日付
        :return: S3 のファイルパス
        """
        if isinstance(date, datetime):
            date = date.strftime("%Y-%m-%d")
        symbol = symbol.replace("/", "_")
        timeframe = f"daily_{timeframe}m"
        return f"{settings.S3_FOLDER_HIST}/{symbol}/{timeframe}/{symbol}_{timeframe}_{date}.parquet"

