import json
from typing import Optional
from functools import lru_cache
from pydantic import BaseModel
from utils.s3_helper import get_s3_helper

CONFIG_FILE = "configs/latest_config.json"

DEFAULT_CONFIG =  {
    "market_symbol": "BTC/JPY",
    "training_period_months": 3,
    "ensemble_ratio": 0.5,
    "epochs": 50,
    "test_ratio": 0.2,
    "feature_lag_X_BB": 5,
    "feature_lag_X_ATR": 15,
    "target_lag_Y": 3
}

class Config(BaseModel):
    """設定情報のスキーマ"""
    market_symbol: str
    training_period_months: int
    ensemble_ratio: float
    epochs: int
    test_ratio: float
    feature_lag_X_BB: int
    feature_lag_X_ATR: int
    target_lag_Y: int

class ConfigManager:
    def __init__(self):
        """S3から設定をロードし、メモリにキャッシュ"""
        self.s3 = get_s3_helper()
        self.load_config()

    def save_config(self, config_data: dict):
        """設定をS3に保存し、キャッシュを更新"""
        self.s3.save_json_to_s3(config_data, CONFIG_FILE)
        self.config_data = config_data  # メモリキャッシュを更新

    def load_config(self) -> Optional[dict]:
        """S3から設定を取得"""
        self.config_data = self.s3.load_json_from_s3(CONFIG_FILE)
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
