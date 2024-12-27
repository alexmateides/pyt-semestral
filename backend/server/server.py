"""
Implementation of uvicorn server
"""
import asyncio
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.logger import Logger
from backend.api.alive import router as alive_router
from backend.api.tapo_320ws import router as tapo_320ws_router
from backend.api.camera import router as camera_router
from backend.utils.movement_listener import movement_listener

API_KEY = 'TEST'


async def lifespan(server_app: FastAPI):
    """
    FastAPI lifespan manager to run movement_listener for the whole duration
    Args:
        server_app:

    Returns:
    """
    server_app.get("/alive")
    # Create a task to run the listener in the background
    task = asyncio.create_task(movement_listener())

    # Yield control to start the application
    yield

    # Clean up tasks when shutting down
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Listener task cancelled")


app = FastAPI(lifespan=lifespan)

# set logger
LOG_LEVEL = 'DEBUG'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, '../..', 'logs')
main_logger = Logger(name='server_logger', path_logs=LOGS_DIR, log_level=LOG_LEVEL).get_main_logger()


@app.middleware("http")
async def catch_all(request: Request, call_next):
    """
    Prevents the server from crashing on unexpected exceptions
    """
    try:
        response = await call_next(request)
        return response
    except Exception as error:
        main_logger.exception(error)


# API Access
@app.middleware("http")
async def api_validate(request: Request, call_next):
    """
    Performs API authentication
    """
    if request.scope["type"] == "websocket":
        return await call_next(request)

    if request.headers.get("api-key") != API_KEY:
        main_logger.info("[SERVER]\tWrong API key")
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    response = await call_next(request)
    return response


# include api routes

# alive ping (mainly used for debugging)
app.include_router(alive_router, prefix="/alive")

# tapo 320ws API
app.include_router(tapo_320ws_router, prefix="/tapo-320ws")

# camera database API
app.include_router(camera_router, prefix="/camera")

# CORS middleware for resource sharing with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Root get
@app.get("/")
async def get_root():
    """
    Returns: Hello World!
    """
    main_logger.info("[SERVER]\t[GET]:root")
    return {"message": "Hello World!"}


# For testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
