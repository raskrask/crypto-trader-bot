import os
import config.environment

class BaseConfig:
    """共通設定"""
    APP_NAME = "CryptTradingBot"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    S3_BUCKET = os.getenv("S3_BUCKET")
    S3_FOLDER_BASE = os.getenv("S3_FOLDER_BASE")
    S3_FOLDER_LIVE = os.getenv("S3_FOLDER_LIVE", f"{S3_FOLDER_BASE}/live_data")
    S3_FOLDER_HIST = os.getenv("S3_FOLDER_HIST", f"{S3_FOLDER_BASE}/historical_data")
    S3_FOLDER_MODEL = os.getenv("S3_FOLDER_MODEL", f"{S3_FOLDER_BASE}/ml_models")
    AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")

class DevelopmentConfig(BaseConfig):
    """開発環境設定"""
    APP_ENV = "development"
    DEBUG = True

class ProductionConfig(BaseConfig):
    """本番環境設定"""
    APP_ENV = "production"
    DEBUG = False

APP_ENV = os.getenv("APP_ENV", "development")

if APP_ENV == "production":
    settings = ProductionConfig()
else:
    settings = DevelopmentConfig()
