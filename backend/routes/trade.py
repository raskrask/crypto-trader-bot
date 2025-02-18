from fastapi import APIRouter, HTTPException, BackgroundTasks
from models.bibyt_trader import BibitTrader

router = APIRouter()
trader = BibitTrader()

@router.get("/test")
async def test_trade():
    return trader.wallet_balance()
