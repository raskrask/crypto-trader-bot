from fastapi import APIRouter
from services.debug_service import DebugService

router = APIRouter()

@router.get("/")
def get_debug_summary():
    """Return diagnostic information from the debug service."""
    return DebugService().do_debug()
