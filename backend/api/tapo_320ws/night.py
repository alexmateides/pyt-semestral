"""
API endpoint for getting/setting camera night-vision status
"""
from asyncio import sleep as asyncio_sleep
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface

router = APIRouter()


@router.get("/night/{name}")
async def get_light_status(name: str) -> JSONResponse:
    """
    Gets light status (ON/OFF) of a camera
    Args:
        name: name of the camera

    Returns: Status of the light
    """
    # connect to interface
    interface = Tapo320WSBaseInterface(name)

    # get light status
    response = interface.get_night_vision_status()

    return JSONResponse(status_code=200, content=response)


@router.post("/night/{name}")
async def change_floodlight_status(name: str) -> JSONResponse:
    """
    Changes floodlight status of a camera (ON/OFF)
    Args:
        name: name of the camera

    Returns: New light status of the camera
    """
    # connect to interface
    interface = Tapo320WSBaseInterface(name)

    # change light status
    interface.change_night_vision_status()

    # sleep to sync the light_status
    await asyncio_sleep(0.3)

    status = interface.get_night_vision_status()

    return JSONResponse(status_code=200, content=status)
