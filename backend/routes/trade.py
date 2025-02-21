from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.bibyt_trader import BibitTrader
from services.auto_trade_service import AutoTradeService

router = APIRouter()

@router.get("/test")
async def test_trade():
    return AutoTradeService().run()
