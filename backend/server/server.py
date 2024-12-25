import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from backend.logger import Logger

from backend.api.alive import router as alive_router
from backend.api.tapo_320ws import router as tapo_320ws_router
from backend.api.camera import router as camera_router

API_KEY = 'TEST'

app = FastAPI()

# set logger
LOG_LEVEL = 'DEBUG'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, '../..', 'logs')
main_logger = Logger(name='server_logger', path_logs=LOGS_DIR, log_level=LOG_LEVEL).get_main_logger()


# API Access
@app.middleware("http")
async def api_validate(request: Request, call_next):
    """

    Performs API authentication

    """
    try:
        if request.headers.get("api-key") != API_KEY:
            main_logger.info(f'[SERVER]\tWrong API key {request.headers}')
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})

        response = await call_next(request)
        return response
    except Exception as error:
        main_logger.error(f'[SERVER]\tAPI verification ERROR {error}')


# add headers for routing
@app.middleware("http")
async def inject_headers(request: Request, call_next):
    """

    Performs API authentication

    """
    try:
        # Default values, could be fetched from a secure storage for production
        client_ip = "192.168.0.152"
        username = "admin"
        password = "admin1"

        # Inject headers into the request state
        request.state.credentials = {
            'x-client-ip': client_ip,
            'x-username': username,
            'x-password': password
        }

        # Log the added headers
        main_logger.info(f"[SERVER] Added Headers: ip={client_ip}, username={username}, password={password}")

        response = await call_next(request)
        return response
    except Exception as error:
        main_logger.error(f'[SERVER]\tHeader injection verification ERROR {error}')


# include api routes
app.include_router(alive_router, prefix="/alive")
app.include_router(tapo_320ws_router, prefix="/tapo-320ws")
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
    try:
        main_logger.info(f'[SERVER]\t[GET]:root')
        return {"message": "Hello World!"}
    except Exception as error:
        main_logger.error(f'[SERVER]\t[GET]: root ERROR')


# For testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
