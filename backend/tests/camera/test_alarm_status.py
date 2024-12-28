"""
tests functionalities of alarm_status module
"""
from backend.camera.tapo_320ws.alarm_status import get_alarm_status


def test_get_alarm_status():
    """
    tests get_alarm_status function
    """
    name = "TestCam"
    status, events = get_alarm_status(name)

    assert status is True
    assert events == [
        {
            "start_time": "00:30:34",
            "end_time": "00:30:40",
            "alarm_type": 6,
            "startRelative": 10,
            "endRelative": 4,
            "camera_name": "TestCam"
        }
    ]
