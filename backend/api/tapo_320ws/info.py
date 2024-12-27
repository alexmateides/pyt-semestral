"""
API endpoint for getting camera information
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface

# route /camera/info
router = APIRouter()


# Retrieve camera info
@router.get("/info/{name}")
async def get_info(name: str) -> JSONResponse:
    """
    Gets information about a camera
    Args:
        name: name of the camera

    Returns: dict - camera information
    """
    # connect to interface
    interface = Tapo320WSBaseInterface(name)

    # retrieve info
    response = interface.get_info()

    return JSONResponse(status_code=200, content=response)
