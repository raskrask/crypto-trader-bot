from typing import Any, Dict

from fastapi import APIRouter

from services.debug_service import DebugService

router = APIRouter()

@router.get("/")
def get_debug_summary() -> Dict[str, Any]:
    """Return diagnostic information gathered from the ML debug pipeline."""

    return DebugService().do_debug()
