import json
from typing import Optional
from functools import lru_cache
from pydantic import BaseModel
from utils.s3_helper import get_s3_helper

CONFIG_FILE = "configs/latest_config.json"

class Config(BaseModel):
    """設定情報のスキーマ"""
    market_symbol: str
    training_period_months: int
    ensemble_ratio: float
    epochs: int
    test_ratio: float

class ConfigManager:
    def __init__(self):
        """S3から設定をロードし、メモリにキャッシュ"""
        self.s3 = get_s3_helper()  # シングルトンS3ヘルパー
        self.config_data = self.load_config() or {}  # デフォルト値をセット

    def save_config(self, config_data: dict):
        """設定をS3に保存し、キャッシュを更新"""
        self.s3.save_json_to_s3(config_data, CONFIG_FILE)
        self.config_data = config_data  # メモリキャッシュを更新

    def load_config(self) -> Optional[dict]:
        """S3から設定を取得"""
        return self.s3.load_json_from_s3(CONFIG_FILE) or {}  # None の場合は空辞書を返す

    def get_config(self) -> dict:
        """メモリキャッシュされた設定を取得"""
        return self.config_data

@lru_cache
def get_config_manager() -> ConfigManager:
    """ConfigManager のシングルトンインスタンスを取得"""
    return ConfigManager()
