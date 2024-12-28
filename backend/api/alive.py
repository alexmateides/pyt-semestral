"""
Alive ping for checking server health
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.utils.logger import Logger


# prefix /alive
router = APIRouter()
logger = Logger('server_logger.api/alive').get_child_logger()


# Simple alive ping
@router.get("/")
async def get_alive():
    """
    Alive ping for checking server health
    """
    logger.info('[GET][/alive]')
    return JSONResponse(status_code=200, content="Alive!")
