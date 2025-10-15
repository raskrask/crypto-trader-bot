import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone
from utils.s3_helper import get_s3_helper
from utils.market_symbol import market_symbol
from config.config_manager import get_config_manager
from models.crypto_training_dataset import CryptoTrainingDataset
from models.exchanges.coincheck_api import CoinCheckAPI
from config.constants import S3_FOLDER_TRADE

class CryptTradeService:
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.s3 = get_s3_helper()
        self.coincheck = CoinCheckAPI()

    def get_balance(self):
        balance = self.coincheck.get_balance()
        ticker = self.coincheck.get_ticker()
        return {"balance": balance, "ticker": ticker}

    def get_transactions(self):
        trade_history = self.coincheck.get_trade_history()
        open_orders = self.coincheck.get_open_orders()
        return {"trade_history": trade_history, "open_orders": open_orders }

    def create_limit_order(self, side, amount, price):
        # !!!! Safty Validate !!!! 
        ticker = self.coincheck.get_ticker()
        rate = ticker.get('last')
        print(f"rate={rate} a={amount} p={price}")
        if amount * rate > 1_000_000 or amount * price > 1_000_000:
            raise Exception( f"取り扱い金額が大きすぎます。{amount} x {price}")
        return self.coincheck.create_limit_order(side, amount, price)

    def get_history_archive(self):
        # 取引履歴を取得
        market = self.config_data.get("market_symbol")
        prefix = f"{S3_FOLDER_TRADE}/{market}_"
        trade_df = pd.DataFrame(list(map(lambda x: self.s3.load_json_from_s3(x), self.s3.get_s3_files(prefix))))
        trade_df["timestamp"] = pd.to_datetime(trade_df["execution_date"]).dt.floor("D")
        #aggregations = {
        #    "execution_price": "sum",
        #    "predicted_price": "mean",
        #    "confidence": "mean"
        #}
        #rade_df = trade_df.groupby("timestamp", as_index=False).agg(aggregations)

        # ohlcvデータを取得
        dataset = CryptoTrainingDataset()
        dataset.start_date = datetime.now(timezone.utc) - timedelta(days=60)
        dataset.end_date = datetime.now(timezone.utc)
        dataset.interval_min = 60 * 24
        ohlcv_df = dataset.get_data()

        # 出力データ加工
        merged_df = ohlcv_df.merge(trade_df, on="timestamp", how="left")
        merged_df.sort_values("timestamp", ascending=True, inplace=True)

        merged_df = merged_df.replace([np.nan, np.inf, -np.inf], None)
        merged_df["predicted_price"] = merged_df["predicted_price"].fillna(0)
        merged_df["execution_price"] = merged_df["execution_price"].fillna(0)
        merged_df.fillna(value="N/A", inplace=True)

        merged_df["unrealized_gains"] = np.where(
            merged_df["prediction_label"].isin([None, "N/A", "HOLD"]), 0,
            merged_df[f"close_{market}"] - merged_df["execution_price"]
        )

        result = {
            "dates": merged_df["timestamp"].dt.strftime("%Y-%m-%d").to_list(),
            "predicted_price": merged_df["predicted_price"].fillna(0).to_list(),
            "purchase_prices": merged_df["execution_price"].fillna(0).to_list(),
            "current_prices": merged_df[f"close_{market}"].to_list(),
            "investment_amounts": merged_df["predicted_price"].fillna(0).to_list(),
            "unrealized_gains": merged_df["unrealized_gains"].to_list(),
            "realized_profits": merged_df["confidence"].astype(object).to_list()
        }

        return result
