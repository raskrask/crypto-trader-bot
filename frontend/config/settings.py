import os

class BaseConfig:
    """共通設定"""
    APP_NAME = "CryptTraderBot"

class DevelopmentConfig(BaseConfig):
    """開発環境設定"""
    APP_ENV = "development"
    DEBUG = True
    API_BASE = "http://backend:8000"

class ProductionConfig(BaseConfig):
    """本番環境設定"""
    APP_ENV = "production"
    DEBUG = False
    API_BASE = "http://xx:8000"

APP_ENV = os.getenv("APP_ENV", "development")

if APP_ENV == "production":
    settings = ProductionConfig()
else:
    settings = DevelopmentConfig()
