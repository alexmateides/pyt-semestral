from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.camera.tapo_320ws.utils import get_auth_by_name

# route /camera/info
router = APIRouter()


# Retrieve camera info
@router.get("/info/{name}")
async def get_info(name: str) -> JSONResponse:
    try:
        # get connection arguments from database
        ip, username, password = get_auth_by_name(name)

        # connect to interface
        interface = Tapo320WSBaseInterface(ip, username, password)

        # retrieve info
        response = interface.get_info()

        return JSONResponse(status_code=200, content=response)

    except Exception as error:
        return NotImplementedError('Error logging for /info currently not implemented')
