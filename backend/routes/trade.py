from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.auto_trade_service import AutoTradeService
from services.trade_history_service import TradeHistoryService

router = APIRouter()

@router.get("/test")
async def test_trade():
    return AutoTradeService().run()

@router.get("/history")
async def history():
    return TradeHistoryService().get_history()
