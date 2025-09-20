from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.eda_service import EdaService

router = APIRouter()

@router.get("/explore")
async def explore():
    return EdaService().explore()

@router.get("/box_market_price ")
async def box_market_price ():
    return EdaService().box_market_price ()