from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.eda_service import EdaService

router = APIRouter()

@router.get("/explore")
async def explore():
    return EdaService().explore()