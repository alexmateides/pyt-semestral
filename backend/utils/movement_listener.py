"""
Utility functions for time
"""
import asyncio
from typing import List
from backend.camera.tapo_320ws.utils import list_tapo_320ws_camera_names
from backend.camera.tapo_320ws.alarm_status import get_alarm_status


async def on_alarm(events: List[dict]) -> None:
    """
    Does something on alarm
    Returns:    None
    """
    print("Alarm!!!")
    print(events)
    return


async def movement_listener():
    """
    Function that listens for alarms

    Returns:

    """
    # listener cooldown -> prevents sending alarms on the same event
    cooldown = 0
    camera_names = list_tapo_320ws_camera_names()

    # listener thread
    while True:
        global_alarm_status = False
        global_events = []

        for camera_name in camera_names:
            # not async -> blocking thread (but quite fast)
            alarm_status, events = get_alarm_status(camera_name)

            # cycle for events from other cameras
            if alarm_status:
                global_alarm_status = True
                global_events.extend(events)

        # do something on alarm
        if global_alarm_status and cooldown <= 0:
            await on_alarm(global_events)
            cooldown = 300

        # wait 10 seconds
        await asyncio.sleep(10)

        # reduce cooldown
        if cooldown > 0:
            cooldown -= 10
