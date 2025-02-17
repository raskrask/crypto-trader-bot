import os
import requests
from fastapi import FastAPI, APIRouter
from config.settings import settings
from routes.ml_train import router as ml_train_router
from routes.ml_evaluate import router as ml_evaluate_router
from routes.config import router as config_router

app = FastAPI()

api_router = APIRouter()
api_router.include_router(ml_train_router, prefix="/ml/train", tags=["ML Train"])
api_router.include_router(ml_evaluate_router, prefix="/ml/evaluate", tags=["ML Evaluation"])
api_router.include_router(config_router, prefix="/config", tags=["ML Config"])

app.include_router(api_router, prefix="/api")


