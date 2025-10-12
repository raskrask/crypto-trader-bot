import json
from typing import Optional
from functools import lru_cache
from pydantic import BaseModel
from utils.s3_helper import get_s3_helper
from config import constants

DEFAULT_CONFIG =  {
    "market_symbol": "btc_jpy",
    "training_period_months": 18,
    "training_timeframe": 1440,
    "ensemble_ratio": 0.5,
    "epochs": 50,
    "test_ratio": 0.2,
    "feature_lag_X_BB": 32,
    "feature_lag_X_ATR": 15,
    "target_buy_term": 15,
    "target_buy_rate": 0.03,
    "target_sell_term": 10,
    "target_sell_rate": 0.01,
    "target_lag_Y": 1,
    "auto_trade_buy_amount": 0.001,
    "auto_trade_sell_amount": 0.001
}

class Config(BaseModel):
    """設定情報のスキーマ"""
    market_symbol: str
    training_period_months: int
    training_timeframe: int
    ensemble_ratio: float
    epochs: int
    test_ratio: float
    feature_lag_X_BB: int
    feature_lag_X_ATR: int
    target_buy_term: int
    target_buy_rate: float
    target_sell_term: int
    target_sell_rate: float
    target_lag_Y: int
    auto_trade_buy_amount: float
    auto_trade_sell_amount: float

class ConfigManager:
    def __init__(self, stage="staging"):
        """S3から設定をロードし、メモリにキャッシュ"""
        self.s3 = get_s3_helper()
        self.stage = stage
        self.load_config()

    def save_config(self, config_data: dict):
        """設定をS3に保存し、キャッシュを更新"""
        key = f"{constants.S3_FOLDER_MODEL}/{self.stage}/config.json"
        self.s3.save_json_to_s3(config_data, key)
        self.config_data = config_data  # メモリキャッシュを更新

    def load_config(self) -> Optional[dict]:
        """S3から設定を取得"""
        key = f"{constants.S3_FOLDER_MODEL}/{self.stage}/config.json"
        self.config_data = self.s3.load_json_from_s3(key) or {}
        for key, value in DEFAULT_CONFIG.items():
            self.config_data.setdefault(key, value)

        return self.config_data

    def get_config(self) -> dict:
        """メモリキャッシュされた設定を取得"""
        return self.config_data


@lru_cache
def get_config_manager() -> ConfigManager:
    """ConfigManager のシングルトンインスタンスを取得"""
    return ConfigManager()
