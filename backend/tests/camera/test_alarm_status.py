"""
tests functionalities of alarm_status module
"""
from datetime import datetime
from app.camera.tapo_320ws.alarm_status import get_alarm_status
from tests.conftest import TAPO_320WS_TEST_DEFAULTS


def test_get_alarm_status():
    """
    tests get_alarm_status function
    """
    name = "TestCam"
    status, alarm_events = get_alarm_status(name)

    # fromtimestamp is system sensitive
    start_time = TAPO_320WS_TEST_DEFAULTS['get_events'][0]['start_time']
    end_time = TAPO_320WS_TEST_DEFAULTS['get_events'][0]['end_time']

    assert status is True
    assert alarm_events == [
        {
            "start_time": datetime.fromtimestamp(start_time).strftime("%H:%M:%S"),
            "end_time": datetime.fromtimestamp(end_time).strftime("%H:%M:%S"),
            "alarm_type": 6,
            "startRelative": 10,
            "endRelative": 4,
            "camera_name": "TestCam"
        }
    ]
