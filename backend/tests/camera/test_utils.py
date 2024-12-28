"""
tests for tapo320ws/utils
"""
from unittest.mock import MagicMock, patch
from app.camera.tapo_320ws.utils import get_auth_by_name, list_tapo_320ws_camera_names
from app.tests.conftest import TEST_CAMERA, TEST_CAMERA2

mock_camera = TEST_CAMERA

mock_auth_row = (
    TEST_CAMERA['ip'],
    TEST_CAMERA['username'],
    TEST_CAMERA['password'],
    TEST_CAMERA['camera_username'],
    TEST_CAMERA['camera_password']
)

mock_name_rows = [
    (TEST_CAMERA['name'],),
    (TEST_CAMERA2['name'],)
]


@patch("app.camera.tapo_320ws.utils.SqliteInterface")
def test_get_auth_by_name(mock_sqlite_interface):
    """
    tests geth_auth_by_name function
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = mock_auth_row

    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    ip, username, password, camera_username, camera_password = get_auth_by_name("TestCam")

    assert ip == TEST_CAMERA['ip']
    assert username == TEST_CAMERA['username']
    assert password == TEST_CAMERA['password']
    assert camera_username == TEST_CAMERA['camera_username']
    assert camera_password == TEST_CAMERA['camera_password']


@patch("app.camera.tapo_320ws.utils.SqliteInterface")
def test_list_tapo_320ws_camera_names(mock_sqlite_interface):
    """
    tests list_tapo_320ws_camera_names function
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.return_value = mock_name_rows

    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    camera_names = list_tapo_320ws_camera_names()

    assert len(camera_names) == 2
    assert camera_names[0] == TEST_CAMERA['name']
    assert camera_names[1] == TEST_CAMERA2['name']
