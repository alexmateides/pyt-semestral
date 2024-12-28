import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from isort.utils import TrieNode

from backend.main import app
from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from backend.database.sqlite_interface import SqliteInterface


@pytest.fixture
def client():
    """
    Provides a FastAPI test client for each test.
    """
    headers = {'api-key': "TEST"}
    return TestClient(app, headers=headers)


# tapo class mock
@pytest.fixture(autouse=True)
def mock_tapo_methods():
    with patch.object(Tapo320WSBaseInterface, "__init__", lambda self, name: None):
        with patch.multiple(
            Tapo320WSBaseInterface,
            get_info=lambda self: {
                "device_info": {
                    "basic_info": {
                        "device_type": "SMART.IPCAMERA",
                        "device_info": "C320WS 2.0 IPC",
                        "features": 3,
                        "device_model": "C320WS",
                        "sw_version": "1.2.1 Build",
                        "device_name": "C320WS 2.0",
                        "hw_version": "1.0",
                        "device_alias": "TestCam",
                        "mac": "D8-DE-44-41-5F-DE",
                        "manufacturer_name": "TP-LINK",
                    }
                }
            },
            change_light_status=lambda self: None,
            change_night_vision_status=lambda self: None,
            get_light_status=lambda self: {
                "status": 0,
                "rest_time": 0
            },
            get_night_vision_status=lambda self: "off",
            get_stream_url=lambda self: "rtsp://admin:admin@192.168.0.123:554/stream1",
            get_time_correction=lambda self: 0,
            get_recordings=lambda self, date: [
                {
                    "startTime": "15:47:43",
                    "endTime": "15:48:50",
                    "vedio_type": 2,
                    "duration_seconds": 67,
                    "date": "2024-12-26",
                    "id": "search_video_results_1"
                },
                {
                    "startTime": "16:02:55",
                    "endTime": "16:04:07",
                    "vedio_type": 2,
                    "duration_seconds": 72,
                    "date": "2024-12-26",
                    "id": "search_video_results_2"
                }
            ],
            get_events=lambda self: [
                {
                    "start_time": 1735342234,
                    "end_time": 1735342240,
                    "alarm_type": 6,
                    "startRelative": 10,
                    "endRelative": 4
                }
            ],
        ):
            yield

# sqlite interface skip init mock
@pytest.fixture(autouse=True)
def mock_sqlite_interface_init():
    with patch.object(SqliteInterface, "__init__", lambda self, name: None):
        yield

