from fastapi import APIRouter
from fastapi.requests import Request
from starlette.responses import JSONResponse

from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.utils.get_auth_headers import get_auth_headers
from asyncio import sleep as asyncio_sleep

# route /camera/info
router = APIRouter()


@router.get("/light")
async def get_light_status(request: Request):
    try:
        # extract headers
        ip, username, password = get_auth_headers(request)

        # connect to interface
        interface = Tapo320WSBaseInterface(ip, username, password)

        # get light status
        response = interface.get_light_status()

        return JSONResponse(status_code=200, content=response)

    except Exception as error:
        return NotImplementedError('Error logging for /info currently not implemented')


# Change camera light status on/off
@router.post("/light")
async def change_floodlight_status(request: Request):
    try:
        # extract headers
        ip, username, password = get_auth_headers(request)

        # connect to interface
        interface = Tapo320WSBaseInterface(ip, username, password)

        # change light status
        interface.change_light_status()

        # sleep to sync the light_status
        await asyncio_sleep(0.3)

        status = interface.get_light_status()

        return JSONResponse(status_code=200, content=status)

    except Exception as error:
        return NotImplementedError('Error logging for /info currently not implemented')
