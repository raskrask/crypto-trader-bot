from fastapi import APIRouter, HTTPException, BackgroundTasks
from services.ml_pipeline_service import MlPipelineService

router = APIRouter()
pipeline = MlPipelineService()

@router.post("/start")
async def start_training(background_tasks: BackgroundTasks):
    """ トレーニング開始API（非同期処理）"""
    if pipeline.training_status["status"] == "In Progress":
        return {"message": "Training is already in progress"}
    
    background_tasks.add_task(pipeline.run_pipeline)
    return {"message": "Training started"}

@router.get("/status")
async def get_training_status():
    """ トレーニングの進行状況を取得 """
    return pipeline.training_status

@router.get("/result")
async def get_training_result():
    """ トレーニング結果を取得 """
    if pipeline.training_status["status"] != "Completed":
        return {"message": "Training is not completed yet"}
    
    return {"result": pipeline.training_status["result"]}
