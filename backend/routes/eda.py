from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.eda_service import EdaService

router = APIRouter()
eda = EdaService()

@router.get("/explore")
async def explore():
    return eda.explore()