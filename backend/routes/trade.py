from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.auto_trade_service import AutoTradeService
from services.crypt_trade_service import CryptTradeService
from services.signal_predictor import SignalPredictor 

router = APIRouter()

class LimitOrderRequest(BaseModel):
    """指値注文リクエスト"""
    side: str = Field(..., description="売買区分。'buy' または 'sell'", example="buy")
    amount: float = Field(..., description="注文数量（BTCなど）")
    price: float = Field(..., description="指値価格（円）")

@router.get("/test")
async def test_trade():
    return AutoTradeService().run()

@router.get("/signals")
async def signals():
    return SignalPredictor().get_predict_signals()

@router.get("/balance")
async def balance():
    return CryptTradeService().get_balance()

@router.get("/transactions")
async def transactions():
    return CryptTradeService().get_transactions()

@router.get("/history")
async def history():
    return CryptTradeService().get_history()

@router.post("/limit_order",
    summary="指値注文を送信する",
    description="指定した価格での買いまたは売り注文を作成します。")
async def limit_order(req: LimitOrderRequest):
    return CryptTradeService().create_limit_order(req.side, req.amount, req.price)
