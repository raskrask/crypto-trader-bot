import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone
from utils.s3_helper import get_s3_helper
from config.config_manager import get_config_manager
from models.crypto_training_dataset import CryptoTrainingDataset
from config import constants

class TradeHistoryService:
    def __init__(self):
        self.config_data = get_config_manager().get_config()
        self.s3 = get_s3_helper()

    def get_history(self):
        

        # 取引履歴を取得
        market = self.config_data.get("market_symbol")
        prefix = f"{constants.S3_FOLDER_TRADE}/{market}_"
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
