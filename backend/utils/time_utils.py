from datetime import datetime, timedelta
from typing import List


def iter_dates(start_date: str, end_date: str) -> List[str]:
    """
    Iterates from start_date to end date by 1 day
    Args:
        start_date: start of the interval given as YYYY-MM-DD
        end_date:   end of the interval given as YYYY-MM-DD

    Returns: List[str] - dates YYYYMMDD format
    """
    # convert to datetime
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    results = []

    # get the dates
    current = start
    while current <= end:
        results.append(str(current.strftime("%Y%m%d")))
        current += timedelta(days=1)

    return results


def timestamp_to_string(timestamp: int) -> str:
    """
    Converts timestamp to human-readable string
    ex. 1735225375 -> 16:02:55
    Args:
        timestamp: timestamp in int format

    Returns: string in HH:MM:SS format
    """
    return datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")


def minute_ago() -> int:
    """
    Returns: timestamp from minute ago
    """
    return int(datetime.timestamp(datetime.now() - timedelta(minutes=1)))
