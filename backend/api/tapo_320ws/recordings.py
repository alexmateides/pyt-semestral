from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.utils.time_utils import iter_dates, timestamp_to_string

# route /camera/info
router = APIRouter()


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
