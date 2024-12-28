"""
API endpoint for listing and downloading camera recordings to the server
"""
from typing import List
import os
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.utils.time_utils import iter_dates, timestamp_to_string
from backend.camera.tapo_320ws.download import download_async
from backend.utils.logger import Logger

# route /camera/info
router = APIRouter()
logger = Logger('server_logger.api/tapo_320ws/recordings').get_child_logger()


class StringList(BaseModel):
    """
    Simple pydantic model for specifying body parameters
    """
    content: List[str]


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

        # format the recordings into human-readable format
        for recording in recordings:
            record_key = list(recording.keys())[0]
            record = recording[record_key]
            record["duration_seconds"] = record["endTime"] - record["startTime"]
            record["date"] = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
            record["id"] = record_key
            record["startTime"] = timestamp_to_string(record["startTime"])
            record["endTime"] = timestamp_to_string(record["endTime"])
            recording[record_key] = record
            tmp_recordings.append(record)

        results.extend(tmp_recordings)

    logger.info('[GET][/tapo-w320s/recordings] %s:\t%s - %s', name, start_date, end_date)
    return JSONResponse(status_code=200, content=results)


@router.post("/recordings/{name}")
async def download_recordings(name: str, date: str, id_list: StringList) -> JSONResponse:
    """
    Downloads recording from camera of {name} to /recordings to be later uploaded to web app
    Args:
        name:       name of the camera

        DATE FORMAT: YYYY-MM-DD
        date:       date of the recordings
        id_list:    id list of the recordings

    Returns:        None
    """
    # format date
    logger.info('[POST][/tapo-w320s/recordings] request -  %s:\t%s', name, date)
    date = datetime.strptime(date, "%Y-%m-%d")
    date = date.strftime("%Y%m%d")

    # connect to interface
    interface = Tapo320WSBaseInterface(name)

    await download_async(interface.tapo_interface, date, id_list.content)

    logger.info('[POST][/tapo-w320s/recordings] downloaded - %s:\t%s', name, date)

    return JSONResponse(status_code=200, content="Recording download successful")

@router.delete("/recordings")
async def delete_recordings() -> JSONResponse:
    """
    Deletes entire /recordings -> should be used after each POST to save space on the server
    Args:
        name:   name of the camera
    Returns:
    """
    recordings_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    recordings_path = os.path.join(recordings_path, "recordings")

    for filename in os.listdir(recordings_path):
        file_path = os.path.join(recordings_path, filename)

        # check if it's recording (.mp4)
        if os.path.isfile(file_path) and filename.endswith('.mp4'):
            # remove the file
            os.remove(file_path)

    logger.info('[DELETE][/tapo-w320s/recordings]')

    return JSONResponse(status_code=200, content="Recording deletion successful")
