"""
API endpoint for opening camera stream websocket
"""
from fastapi import APIRouter, WebSocket, WebSocketException, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from app.camera.tapo_320ws.video_stream import RTSPStreamer
from app.utils.logger import Logger

# route /camera/stream
router = APIRouter()
streamer = RTSPStreamer()
logger = Logger('server_logger.api/tapo_320ws/stream').get_child_logger()


# Retrieve camera info
@router.get("/stream/{name}")
async def get_stream_url(name: str) -> JSONResponse:
    """
    Gets WebSocket URL for streaming
    Args:
        name: name of the camera
    Returns: dict with WebSocket URL
    """
    # Generate the WebSocket URL for the client
    ws_url = f"ws://localhost:8000/tapo-320ws/stream/ws/{name}"

    logger.info('[GET][/tapo-w320s/stream] %s', name)

    return JSONResponse(status_code=200, content={"streamUrl": ws_url})


@router.websocket("/stream/ws/{name}")
async def websocket_stream(websocket: WebSocket, name: str):
    """
    Streams video frames for a given camera via WebSocket
    Args:
        websocket: WebSocket connection
        name: name of the camera
    """
    try:
        logger.info('[WEBSOCKET][/tapo-w320s/stream] %s', name)
        await websocket.accept()

        # retrieve RTSP URL for camera name
        interface = Tapo320WSBaseInterface(name)
        rtsp_url = interface.get_stream_url()

        # add client to the RTSPStreamer
        streamer.add_client(rtsp_url, websocket)

        # keep WebSocket connection alive
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect as disconnect_error:
        logger.info('[WEBSOCKET][/tapo-w320s/stream] %s - client dicsonnected: %s, %s', name, disconnect_error.code,
                    disconnect_error.reason)

    except WebSocketException as error:
        # remove client from the RTSPStreamer
        logger.error('[WEBSOCKET][/tapo-w320s/stream] %s = "WebSocket Error: %s ', name, error)
        streamer.remove_client(rtsp_url, websocket)
        return JSONResponse(status_code=500, content={f"WebSocket Error:\t{error}"})
