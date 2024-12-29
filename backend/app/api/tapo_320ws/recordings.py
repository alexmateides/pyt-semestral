"""
API endpoint for listing and downloading camera recordings to the server
"""
import os
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from app.camera.tapo_320ws.utils import get_downloaded_recordings
from app.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from app.utils.time_utils import iter_dates, timestamp_to_string
from app.camera.tapo_320ws.download import download_async
from app.utils.logger import Logger

# route /camera/info
router = APIRouter()
logger = Logger('server_logger.api/tapo_320ws/recordings').get_child_logger()

# get /backend/recordings
RECORDINGS_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
RECORDINGS_PATH = os.path.join(RECORDINGS_PATH, 'recordings')


class DownloadRecordingsBody(BaseModel):
    """
    pydantic body model for API calls
    """
    id: str
    date: str


# Retrieve camera info
@router.get("/recordings/{name}")
async def get_recordings(name: str, start_date: str, end_date: str) -> JSONResponse:
    """
    Gets information about a camera
    Args:
        name: name of the camera

        DATE FORMAT: YYYY-MM-DD
        start_date: start of the interval
        end_date: end of the interval

    Returns: List[recordings]
    """
    # connect to interface
    interface = Tapo320WSBaseInterface(name)

    date_interval = iter_dates(start_date, end_date)

    # get the recordings for the interval
    results = []
    for date in date_interval:
        recordings = interface.get_recordings(date)

        tmp_recordings = []

        downloaded_recordings = get_downloaded_recordings(name, RECORDINGS_PATH)

        # format the recordings into human-readable format
        for recording in recordings:
            record_key = list(recording.keys())[0]
            record = recording[record_key]
            record["duration_seconds"] = record["endTime"] - record["startTime"]
            record["date"] = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
            record["id"] = record_key
            record["startTime"] = timestamp_to_string(record["startTime"])
            record["endTime"] = timestamp_to_string(record["endTime"])
            record["downloaded"] = f"{record['date']}____{record['id']}" in downloaded_recordings
            recording[record_key] = record
            tmp_recordings.append(record)

        results.extend(tmp_recordings)

    logger.info('[GET][/tapo-w320s/recordings] %s:\t%s - %s', name, start_date, end_date)
    return JSONResponse(status_code=200, content=results)


@router.post("/recordings/{name}")
async def download_recordings(name: str, body: DownloadRecordingsBody) -> JSONResponse:
    """
    Downloads recording from camera of {name} to /recordings to be later uploaded to web app
    Args:
        name:       name of the camera

        DATE FORMAT: YYYY-MM-DD
        date:       date of the recordings
        id:         id of the recording

    Returns:        None
    """
    # format date
    logger.info('[POST][/tapo-w320s/recordings] request -  %s:\t%s', name, body.date)
    date = datetime.strptime(body.date, "%Y-%m-%d")
    date = date.strftime("%Y%m%d")

    # connect to interface
    interface = Tapo320WSBaseInterface(name)

    await download_async(interface.tapo_interface, name, date, body.id)

    logger.info('[POST][/tapo-w320s/recordings] downloaded - %s:\t%s', name, body.date)

    return JSONResponse(status_code=200, content="Recording download successful")


@router.delete("/recordings")
async def delete_recordings() -> JSONResponse:
    """
    Deletes entire /recordings -> should be used after each POST to save space on the server
    Args:
        name:   name of the camera
    Returns:
    """
    for filename in os.listdir(RECORDINGS_PATH):
        file_path = os.path.join(RECORDINGS_PATH, filename)

        # check if it's recording (.mp4)
        if os.path.isfile(file_path) and filename.endswith('.mp4'):
            # remove the file
            os.remove(file_path)

    logger.info('[DELETE][/tapo-w320s/recordings]')

    return JSONResponse(status_code=200, content="Recording deletion successful")


@router.post("/recordings/download/{name}")
async def get_recordings_download(name: str, body: DownloadRecordingsBody) -> FileResponse:
    """
    Downloads a recording to client
    name:   name of the camera
    body:   body parameters of recording
    """
    recording_date = body.date
    recording_id = body.id

    recording_filename = f"{name}____{recording_date}____{recording_id}.mp4"
    recording_file_path = os.path.join(RECORDINGS_PATH, recording_filename)

    # recording is already downloaded to server
    if os.path.isfile(recording_file_path):
        logger.info("Recording %s sent to client", recording_filename)
        return FileResponse(
            recording_file_path,
            media_type="video/mp4",
            filename=recording_filename,
        )

    # recording needs to be downloaded to server
    interface = Tapo320WSBaseInterface(name)

    # format the date to YYYYMMDD
    recording_date = datetime.strptime(recording_date, "%Y-%m-%d")
    recording_date = recording_date.strftime("%Y%m%d")
    logger.info("Downloading %s to server", recording_filename)
    await download_async(interface.tapo_interface, name, recording_date, recording_id)

    # send the file to client
    if os.path.isfile(recording_file_path):
        logger.info("Recording %s sent to client", recording_filename)
        return FileResponse(
            recording_file_path,
            media_type="video/mp4",
            filename=recording_filename,
        )

    logger.error("Downloading of %s failed", recording_filename)
    return HTTPException(status_code=404, detail="Recording download failed")
