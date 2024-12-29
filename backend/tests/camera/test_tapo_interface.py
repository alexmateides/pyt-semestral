"""
tests Tapo320WSBaseInterface class against base set in conftest.py
"""
from unittest.mock import patch
from app.camera.tapo_320ws.interface import Tapo320WSBaseInterface
from tests.conftest import TAPO_320WS_TEST_DEFAULTS


def test_get_info():
    """
    get_info tester
    """
    interface = Tapo320WSBaseInterface("TestCam")
    info = interface.get_info()
    assert info == TAPO_320WS_TEST_DEFAULTS["get_info"]


def test_change_light_status():
    """
    change_light_status tester
    """
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.change_light_status() == TAPO_320WS_TEST_DEFAULTS["change_light_status"]


def test_change_night_vision_light_status():
    """
    change_night_vision_light_status tester
    """
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.change_night_vision_status() == TAPO_320WS_TEST_DEFAULTS["change_night_vision_status"]


@patch("app.camera.tapo_320ws.interface.Tapo320WSBaseInterface.get_light_status")
def test_get_light_status(mock_get_light_status):
    """
    get_light_status tester
    """

    mock_get_light_status.return_value = TAPO_320WS_TEST_DEFAULTS["get_light_status"]

    interface = Tapo320WSBaseInterface("TestCam")
    result = interface.get_light_status()

    mock_get_light_status.assert_called_once()
    assert result == TAPO_320WS_TEST_DEFAULTS["get_light_status"]


def test_get_night_vision_status():
    """
    get_night_vision_status tester
    """
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.get_night_vision_status() == TAPO_320WS_TEST_DEFAULTS["get_night_vision_status"]


def test_get_stream_url():
    """
    get_stream_url tester
    """
    interface = Tapo320WSBaseInterface("TestCam")
    stream_url = interface.get_stream_url()
    assert stream_url == TAPO_320WS_TEST_DEFAULTS["get_stream_url"]


def test_get_time_correction():
    """
    get_time_correction tester
    """
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.get_time_correction() == TAPO_320WS_TEST_DEFAULTS["get_time_correction"]


def test_get_recordings():
    """
    get_recordings tester
    """
    interface = Tapo320WSBaseInterface("TestCam")
    recordings = interface.get_recordings("2024-12-26")
    assert len(recordings) == 2
    assert recordings == TAPO_320WS_TEST_DEFAULTS["get_recordings"]
