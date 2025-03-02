import traceback
from fastapi import APIRouter, HTTPException
from services.ml_evaluate_service import MlEvaluteService

router = APIRouter()

@router.get("/predictions")
def get_predictions():
    """過去の実際の価格と、現在のモデル・新しいモデルの予測結果を取得"""
    try:
        data = MlEvaluteService().get_predictions()
        return data
    except Exception as e:
        print( traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/promote_model")
def promote_model():
    """新しいモデルを本番環境に適用"""
    try:
        MlEvaluteService().promote_model()
        return {"message": "新しいモデルが本番環境に適用されました"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
