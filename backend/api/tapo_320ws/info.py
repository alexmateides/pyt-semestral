from fastapi import APIRouter
from fastapi.requests import Request
from starlette.responses import JSONResponse

from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.utils.get_auth_headers import get_auth_headers

# route /camera/info
router = APIRouter()


# Retrieve camera info
@router.get("/info")
async def get_info(request: Request):
    try:
        # extract headers
        ip, username, password = get_auth_headers(request)

        # connect to interface
        interface = Tapo320WSBaseInterface(ip, username, password)

        # retrieve info
        response = interface.get_info()

        return JSONResponse(status_code=200, content=response)

    except Exception as error:
        return NotImplementedError('Error logging for /info currently not implemented')
