import os
import requests
from fastapi import FastAPI, APIRouter
from config.settings import settings
from routes.ml_train import router as ml_train_router
from routes.ml_evalute import router as ml_evalute_router
from routes.config import router as config_router

app = FastAPI()

api_router = APIRouter()
api_router.include_router(ml_train_router, prefix="/ml/train", tags=["ML Train"])
api_router.include_router(ml_evalute_router, prefix="/ml/evalute", tags=["ML Evalution"])
api_router.include_router(config_router, prefix="/config", tags=["ML Config"])

app.include_router(api_router, prefix="/api")


