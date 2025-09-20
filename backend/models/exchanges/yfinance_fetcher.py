import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
import os

class YFinanceFetcher:
    def __init__(self, cache_dir="tmp"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_path(self, symbol, year, month):
        return os.path.join(self.cache_dir, f"{symbol}_{year}_{month:02d}.csv")

    def fetch_month(self, symbol, year, month):
        """
        指定月の株価を取得
        前月以前はキャッシュを使う
        当月は常に最新取得
        """
        today = datetime.today()
        is_current_month = (today.year == year and today.month == month)
        cache_file = self._get_cache_path(symbol, year, month)

        # キャッシュがある場合、当月以外は読み込む
        if not is_current_month and os.path.exists(cache_file):
            df = pd.read_csv(cache_file, parse_dates=["Date"], index_col="Date")
            return df

        # 期間指定
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        end_date = min(end_date, today)

        # yfinance で取得
        ticker = yf.Ticker(symbol)
        chunk_days = 30
        chunk_start = start_date
        dfs = []

        while chunk_start < end_date:
            chunk_end = min(chunk_start + timedelta(days=chunk_days), end_date)
            df_chunk = ticker.history(start=chunk_start.strftime("%Y-%m-%d"),
                                      end=chunk_end.strftime("%Y-%m-%d"),
                                      interval="1d")
            dfs.append(df_chunk)
            chunk_start = chunk_end
            time.sleep(1.5)

        df_full = pd.concat(dfs)
        df_full = df_full[~df_full.index.duplicated()]

        # キャッシュ保存（当月以外のみ）
        if not is_current_month:
            df_full.to_csv(cache_file)

        return df_full

    def fetch_last_n_months(self, symbol, n=12):
        """
        過去 n ヶ月分のデータを取得して結合
        """
        today = datetime.today()
        dfs = []
        for i in range(n):
            month = (today.month - i - 1) % 12 + 1
            year = today.year - ((i + 12 - today.month) // 12)
            df_month = self.fetch_month(symbol, year, month)
            dfs.append(df_month)
        df_all = pd.concat(dfs)
        df_all = df_all[~df_all.index.duplicated()]

        df_all = df_all.sort_index()
        df_all = df_all.sort_index()
        df_all = df_all.reset_index().rename(columns={"Date": "timestamp"})
        df_all = df_all.rename(columns={ "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume" })

        return df_all
