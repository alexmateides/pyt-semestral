from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.camera.tapo_320ws.utils import get_auth_by_name
from backend.camera.tapo_320ws.video_stream import RTSPStreamer

# route /camera/stream
router = APIRouter()
streamer = RTSPStreamer()


# Retrieve camera info
@router.get("/stream/{name}")
async def get_stream_url(name: str) -> JSONResponse:
    """
    Gets WebSocket URL for streaming
    Args:
        name: name of the camera
    Returns: dict with WebSocket URL
    """
    try:
        # Generate the WebSocket URL for the client
        ws_url = f"ws://localhost:8000/tapo-320ws/stream/ws/{name}"
        return JSONResponse(status_code=200, content={"streamUrl": ws_url})
    except Exception as error:
        return JSONResponse(status_code=500, content={"error": str(error)})


@router.websocket("/stream/ws/{name}")
async def websocket_stream(websocket: WebSocket, name: str):
    """
    Streams video frames for a given camera via WebSocket
    Args:
        websocket: WebSocket connection
        name: name of the camera
    """
    await websocket.accept()

    try:
        # Retrieve the RTSP URL for the given camera name
        ip, username, password = get_auth_by_name(name)  # Custom logic to get camera credentials
        interface = Tapo320WSBaseInterface(ip, username, password)
        rtsp_url = interface.get_stream_url()

        print(rtsp_url)

        # Add the client to the RTSPStreamer
        streamer.add_client(rtsp_url, websocket)

        # Keep the WebSocket connection alive
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        # Remove the client from the RTSPStreamer
        streamer.remove_client(rtsp_url, websocket)

    except Exception as error:
        print(f"Error: {error}")
        await websocket.close()
