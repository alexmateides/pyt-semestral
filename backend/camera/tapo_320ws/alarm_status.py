from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.utils.time_utils import timestamp_to_string
from typing import Tuple, List


def get_alarm_status(name: str) -> Tuple[bool, List[dict]]:
    """
    Gets alarm status for camera with name=name from SQL database
    Args:
        name: camera name

    Returns:
        False, [] if no alarm
        True, [events] if alarm
    """
    interface = Tapo320WSBaseInterface(name)

    events = interface.get_events()

    # no alarm
    if len(events) == 0:
        return False, []

    # transform events into human-readable format
    for event in events:
        event['start_time'] = timestamp_to_string(event['start_time'])
        event['end_time'] = timestamp_to_string(event['end_time'])
        event['camera_name'] = name

    return True, events
