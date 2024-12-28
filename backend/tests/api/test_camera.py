"""
/camera endpoint tests
"""
from unittest.mock import MagicMock, patch

from backend.tests.conftest import TEST_CAMERA

# mock data
mock_camera = TEST_CAMERA
mock_camera_row = (
    "TestCam", "Tapo320WS", "192.168.0.123", "admin", "admin123", "camera_user", "camera_pass"
)


@patch("backend.api.camera.SqliteInterface")
def test_get_all_cameras(mock_sqlite_interface, client):
    """
    tests GET /camera
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.return_value = [mock_camera_row]
    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    response = client.get("/camera")
    expected_response = [TEST_CAMERA]
    assert response.status_code == 200
    assert response.json() == expected_response


@patch("backend.api.camera.SqliteInterface")
def test_add_new_camera(mock_sqlite_interface, client):
    """
    tests POST /camera
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None
    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    response = client.post("/camera", json=mock_camera)
    assert response.status_code == 200
    assert response.json() == {"response": "Camera TestCam created successfully"}


@patch("backend.api.camera.SqliteInterface")
def test_update_existing_camera(mock_sqlite_interface, client):
    """
    tests POST /camera
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = mock_camera_row
    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    updated_camera = mock_camera.copy()
    updated_camera["ip"] = "192.168.0.124"

    response = client.post("/camera", json=updated_camera)
    assert response.status_code == 200
    assert response.json() == {"response": "Camera TestCam updated successfully"}


@patch("backend.api.camera.SqliteInterface")
def test_delete_existing_camera(mock_sqlite_interface, client):
    """
    test DELETE /camera
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = mock_camera_row
    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    response = client.delete("/camera", params={"name": "TestCam"})
    assert response.status_code == 200
    assert response.json() == {"response": "Camera TestCam deleted successfully"}


@patch("backend.api.camera.SqliteInterface")
def test_delete_nonexistent_camera(mock_sqlite_interface, client):
    """
    test DELETE /camera failure
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None
    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    response = client.delete("/camera", params={"name": "TestCam2"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Camera TestCam2 not found"}


@patch("backend.api.camera.SqliteInterface")
def test_get_camera_by_name(mock_sqlite_interface, client):
    """
    tests GET /camera/name
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = mock_camera_row
    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    response = client.get("/camera/TestCam")
    expected_response = TEST_CAMERA
    assert response.status_code == 200
    assert response.json() == expected_response


@patch("backend.api.camera.SqliteInterface")
def test_get_nonexistent_camera_by_name(mock_sqlite_interface, client):
    """
    test GET /camera failure
    """
    mock_cursor = MagicMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None
    mock_instance = mock_sqlite_interface.return_value
    mock_instance.cursor = mock_cursor

    response = client.get("/camera/TestCam2")
    assert response.status_code == 404
    assert response.json() == {"detail": "Camera TestCam2 not found"}
