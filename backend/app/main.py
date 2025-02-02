"""
Implementation of uvicorn server
"""
import os
import asyncio
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
from dotenv import load_dotenv, find_dotenv

from app.utils.logger import Logger
from app.api.alive import router as alive_router
from app.api.tapo_320ws import router as tapo_320ws_router
from app.api.camera import router as camera_router
from app.utils.movement_listener import movement_listener

load_dotenv(find_dotenv())

API_KEY = os.getenv("API_KEY")
FRONTEND_URL = os.getenv("FRONTEND_URL")


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """
    FastAPI lifespan manager to run movement_listener for the whole duration
    Args:

    Returns:
    """
    fastapi_app.get('/alive')
    # Create a task to run the listener in the background
    task = asyncio.create_task(movement_listener())

    # Yield control to start the application
    yield

    # Clean up tasks when shutting down
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        main_logger.info("Listener task cancelled")


app = FastAPI(lifespan=lifespan)

# set logger
LOG_LEVEL = 'DEBUG'
main_logger = Logger(name='server_logger', log_level=LOG_LEVEL).get_main_logger()


@app.middleware("http")
async def handle_exceptions(request: Request, call_next):
    """
    Exception handling middleware
    """
    try:
        response = await call_next(request)
        return response

    # propagates exceptions
    except HTTPException as error:
        raise error

    # catches all other unhandled exceptions -> prevents server crash
    except Exception as error:
        main_logger.critical("Unhandled exception", exc_info=error)


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


# Include api routes
# ------------------
# alive ping (mainly used for debugging)
app.include_router(alive_router, prefix="/alive")

# tapo 320ws API
app.include_router(tapo_320ws_router, prefix="/tapo-320ws")

# camera database API
app.include_router(camera_router, prefix="/camera")

# CORS middleware for resource sharing with frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
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
