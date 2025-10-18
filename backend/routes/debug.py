from fastapi import APIRouter
from services.debug_service import DebugService

router = APIRouter()

@router.get("/")
def get_debug_summary():
    return DebugService().do_debug()
