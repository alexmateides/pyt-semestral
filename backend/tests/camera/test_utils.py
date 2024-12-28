from unittest.mock import MagicMock, patch
from backend.camera.tapo_320ws.utils import get_auth_by_name, list_tapo_320ws_camera_names

mock_camera = {
    "name": "TestCam",
    "model": "Tapo320WS",
    "ip": "192.168.0.123",
    "username": "admin",
    "password": "admin123",
    "camera_username": "camera_user",
    "camera_password": "camera_pass"
}

mock_auth_row = (
    "192.168.0.123", "admin", "admin123", "camera_user", "camera_pass"
)

mock_name_rows = [
    ("TestCam",),
    ("TestCam2",)
]


@patch("backend.camera.tapo_320ws.utils.SqliteInterface")
def test_get_auth_by_name(mock_sqlite_interface):
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = mock_auth_row

    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    ip, username, password, camera_username, camera_password = get_auth_by_name("TestCam")

    assert ip == "192.168.0.123"
    assert username == "admin"
    assert password == "admin123"
    assert camera_username == "camera_user"
    assert camera_password == "camera_pass"


@patch("backend.camera.tapo_320ws.utils.SqliteInterface")
def test_list_tapo_320ws_camera_names(mock_sqlite_interface):
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.return_value = mock_name_rows

    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    camera_names = list_tapo_320ws_camera_names()

    assert len(camera_names) == 2
    assert camera_names[0] == "TestCam"
    assert camera_names[1] == "TestCam2"
