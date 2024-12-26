from fastapi import APIRouter
from fastapi.responses import JSONResponse
from typing import List
import os
from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.utils.time_utils import iter_dates, timestamp_to_string
from backend.camera.tapo_320ws.download import download_async
from datetime import datetime
from pydantic import BaseModel
import asyncio

# route /camera/info
router = APIRouter()


class StringList(BaseModel):
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
    try:
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
                record["duration_seconds"] = (record["endTime"] - record["startTime"])
                record["date"] = f"{date[0:4]}-{date[4:6]}-{date[6:8]}"
                record["id"] = record_key
                record["startTime"] = timestamp_to_string(record["startTime"])
                record["endTime"] = timestamp_to_string(record["endTime"])
                recording[record_key] = record
                tmp_recordings.append(record)

            results.extend(tmp_recordings)

        return JSONResponse(status_code=200, content=results)

    except Exception as error:
        return NotImplementedError('Error logging for /recordings currently not implemented')


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
    try:
        # format date
        date = datetime.strptime(date, "%Y-%m-%d")
        date = date.strftime("%Y%m%d")

        # connect to interface
        interface = Tapo320WSBaseInterface(name)

        await download_async(interface.tapo_interface, date, id_list.content)

        return JSONResponse(status_code=200, content="Recording download successful")

    except Exception as error:
        print(error)
        raise NotImplementedError('Error logging for /recordings currently not implemented')


@router.delete("/recordings")
async def delete_recordings() -> JSONResponse:
    """
    Deletes entire /recordings -> should be used after each POST to save space on the server
    Args:
        name:   name of the camera
    Returns:
    """
    try:
        recordings_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        recordings_path = os.path.join(recordings_path, "recordings")

        for filename in os.listdir(recordings_path):
            file_path = os.path.join(recordings_path, filename)

            # check if it's recording (.mp4)
            if os.path.isfile(file_path) and filename.endswith('.mp4'):
                # remove the file
                os.remove(file_path)

        return JSONResponse(status_code=200, content="Recording deletion successful")

    except Exception as error:
        raise NotImplementedError('Error logging for /recordings currently not implemented')
