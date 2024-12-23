import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from backend.api import alive
import os
from backend.logger import Logger

API_KEY = 'TEST'

app = FastAPI()

# set logger
LOG_LEVEL='INFO'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, '../..', 'logs')
main_logger = Logger(name='server_logger', path_logs=LOGS_DIR, log_level=LOG_LEVEL).get_main_logger()

# include api routes
app.include_router(alive.router, prefix="/alive")


# API Access
@app.middleware("http")
async def api_validate(request: Request, call_next):
    """

    Performs API authentication

    """
    try:
        if request.headers.get("api-key") != API_KEY:
            main_logger.info(f'[SERVER]\tWrong API key {request}')
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})
        response = await call_next(request)
        return response
    except Exception as error:
        main_logger.error(f'[SERVER]\tAPI verification ERROR')


# Root get
@app.get("/")
async def get_root():
    try:
        main_logger.info(f'[SERVER]\t[GET]:root')
        return {"message": "Hello World!"}
    except Exception as error:
        main_logger.errpr(f'[SERVER]\t[GET]: root ERROR')


# For testing
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
