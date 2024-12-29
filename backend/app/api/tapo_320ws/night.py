"""
API endpoint for getting/setting camera night-vision status
"""
from asyncio import sleep as asyncio_sleep
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from app.utils.logger import Logger

router = APIRouter()
logger = Logger('server_logger.api/tapo_320ws/night').get_child_logger()


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
    status = interface.get_night_vision_status()

    if status in ('off', 'auto'):
        status = {'status': 0}
    else:
        status = {'status': 1}

    logger.info('[GET][/tapo-w320s/night] %s', name)

    return JSONResponse(status_code=200, content=status)


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

    # get old status

    status = interface.get_night_vision_status()

    if status in ('off', 'auto'):
        status = {'status': 1}
    else:
        status = {'status': 0}

    # change light status
    interface.change_night_vision_status()

    logger.info('[POST][/tapo-w320s/night] %s', name)

    return JSONResponse(status_code=200, content=status)
