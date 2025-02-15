from fastapi import APIRouter
from config.config_manager import get_config_manager, Config

router = APIRouter()
config_manager = get_config_manager()

# 設定を保存するAPI
@router.post("/")
def save_config(config: Config):
    config_data = config.dict()
    config_manager.save_config(config_data)
    return {"message": "設定が保存されました"}

# 設定を取得するAPI
@router.get("/")
def get_config():
    return config_manager.get_config()
