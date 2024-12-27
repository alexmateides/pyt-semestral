"""
Alive ping for checking server health
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

# prefix /alive
router = APIRouter()


# Simple alive ping
@router.get("/")
async def get_alive():
    """
    Alive ping for checking server health
    """
    return JSONResponse(status_code=200, content="Alive!")
