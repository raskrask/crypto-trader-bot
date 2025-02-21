import os
import config.environment
import pandas as pd

class BaseSettings:
    """共通設定"""
    APP_NAME = "CryptTradingBot"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
    S3_BUCKET = os.getenv("S3_BUCKET")

    BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
    BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
    BYBIT_BASE_URL = os.getenv("BYBIT_BASE_URL")

    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

class DevelopmentSettings(BaseSettings):
    """開発環境設定"""
    APP_ENV = "development"
    DEBUG = True
    pd.set_option("display.max_columns", None)

class ProductionSettings(BaseSettings):
    """本番環境設定"""
    APP_ENV = "production"
    DEBUG = False

APP_ENV = os.getenv("APP_ENV", "development")

if APP_ENV == "production":
    settings = ProductionSettings()
else:
    settings = DevelopmentSettings()
