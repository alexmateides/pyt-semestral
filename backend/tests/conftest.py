"""
Pytest configuration file
"""
import os
from unittest.mock import patch
import pytest
from dotenv import load_dotenv, find_dotenv
from fastapi.testclient import TestClient
from app.main import app
from app.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from app.database.sqlite_interface import SqliteInterface
from typing_extensions import override

load_dotenv(find_dotenv())
API_KEY = os.getenv("API_KEY")

@pytest.fixture
def client():
    """
    Provides a FastAPI test client for each test.
    """
    headers = {'api-key': API_KEY}
    return TestClient(app, headers=headers)


# sample test camera
TEST_CAMERA = {
    "name": "TestCam",
    "model": "Tapo320WS",
    "ip": "192.168.0.123",
    "username": "admin",
    "password": "admin123",
    "camera_username": "camera_user",
    "camera_password": "camera_pass"
}

TEST_CAMERA2 = {
    "name": "TestCam2",
    "model": "Tapo320WS",
    "ip": "192.168.0.124",
    "username": "admin",
    "password": "admin123",
    "camera_username": "camera_user",
    "camera_password": "camera_pass"
}

# default values for tests
TAPO_320WS_TEST_DEFAULTS = {
    'get_info': {
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
    'change_light_status': None,
    'change_night_vision_status': None,
    'get_light_status': {
        "status": 0,
        "rest_time": 0
    },
    'get_night_vision_status': 'off',
    'get_stream_url': "rtsp://admin:admin@192.168.0.123:554/stream1",
    'get_time_correction': 0,
    'get_recordings': [
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
    'get_events': [
        {
            "start_time": 1735342234,
            "end_time": 1735342240,
            "alarm_type": 6,
            "startRelative": 10,
            "endRelative": 4
        }
    ]

}


# tapo class mock
@pytest.fixture(autouse=True)
def mock_tapo_320ws_methods():
    """
    Mocks methods of Tapo_320WSBaseInterface
    """
    with patch.object(Tapo320WSBaseInterface, "__init__", lambda self, name: None):
        with patch.multiple(
                Tapo320WSBaseInterface,
                get_info=lambda self: TAPO_320WS_TEST_DEFAULTS["get_info"],
                change_light_status=lambda self: TAPO_320WS_TEST_DEFAULTS["change_light_status"],
                change_night_vision_status=lambda self: TAPO_320WS_TEST_DEFAULTS["change_night_vision_status"],
                get_light_status=lambda self: TAPO_320WS_TEST_DEFAULTS["get_light_status"],
                get_night_vision_status=lambda self: TAPO_320WS_TEST_DEFAULTS["get_night_vision_status"],
                get_stream_url=lambda self: TAPO_320WS_TEST_DEFAULTS["get_stream_url"],
                get_time_correction=lambda self: TAPO_320WS_TEST_DEFAULTS["get_time_correction"],
                get_recordings=lambda self, date: TAPO_320WS_TEST_DEFAULTS["get_recordings"],
                get_events=lambda self: TAPO_320WS_TEST_DEFAULTS["get_events"],
        ):
            yield


# sqlite interface skip init mock
@pytest.fixture(autouse=True)
def mock_sqlite_interface_init():
    """
    Disables __init__ of sqlite interface which prevents connection to real sqlite database which would raise multithreading error during testing
    """
    with patch.object(SqliteInterface, "__init__", lambda self, name: None):
        yield
