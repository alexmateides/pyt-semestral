from unittest.mock import patch
from fastapi.exceptions import HTTPException


@patch("backend.api.tapo_320ws.recordings.Tapo320WSBaseInterface")
@patch("backend.api.tapo_320ws.recordings.iter_dates")
def test_get_recordings_success(mock_camera_class, mock_iter_dates, client):
    mock_camera_instance = mock_camera_class.return_value
    mock_iter_dates.return_value = ["20240101", "20240102"]

    assert mock_camera_instance is not None, "Mock camera instance is None"

    mock_camera_instance.get_recordings.return_value = [
        {"recording1": {"startTime": 1609459200, "endTime": 1609462800}},
        {"recording2": {"startTime": 1609466400, "endTime": 1609470000}},
    ]

    response = client.get("/tapo-320ws/recordings/TestCam?start_date=2024-01-01&end_date=2024-01-02")

    assert response.status_code == 200


@patch("backend.api.tapo_320ws.recordings.Tapo320WSBaseInterface")
def test_get_recordings_fail(mock_camera_class, client):
    mock_camera_class.side_effect = HTTPException(status_code=404, detail="Camera not found")

    response = client.get("/tapo-320ws/recordings/InvalidCam?start_date=2024-01-01&end_date=2024-01-02")

    assert response.status_code == 404
    assert response.json() == {"detail": "Camera not found"}


@patch("backend.api.tapo_320ws.recordings.Tapo320WSBaseInterface")
@patch("backend.api.tapo_320ws.recordings.download_async")
def test_post_download_recordings_success(mock_download_async, mock_camera_class, client):
    mock_camera_instance = mock_camera_class.return_value
    mock_download_async.return_value = None

    response = client.post(
        "/tapo-320ws/recordings/TestCam",
        json={"content": ["recording1", "recording2"]},
        params={"date": "2024-01-01"}
    )

    assert response.status_code == 200
    assert response.json() == "Recording download successful"
    mock_download_async.assert_called_once()


@patch("backend.api.tapo_320ws.recordings.Tapo320WSBaseInterface")
@patch("backend.api.tapo_320ws.recordings.download_async")
def test_post_download_recordings_fail(mock_download_async, mock_camera_class, client):
    mock_camera_class.side_effect = HTTPException(status_code=404, detail="Camera not found")

    response = client.post(
        "/tapo-320ws/recordings/InvalidCam",
        json={"content": ["recording1", "recording2"]},
        params={"date": "2024-01-01"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Camera not found"}
    mock_download_async.assert_not_called()


@patch("backend.api.tapo_320ws.recordings.os")
def test_delete_recordings_success(mock_os, client):
    mock_os.listdir.return_value = ["recording1.mp4", "recording2.mp4"]
    mock_os.path.isfile.return_value = True
    mock_os.path.dirname.return_value = "/mock/tapo-320ws/recordings"

    response = client.delete("/tapo-320ws/recordings")

    assert response.status_code == 200
    assert response.json() == "Recording deletion successful"
    assert mock_os.remove.call_count == 2


@patch("backend.api.tapo_320ws.recordings.os")
def test_delete_recordings_no_files(mock_os, client):
    mock_os.listdir.return_value = []
    mock_os.path.isfile.return_value = False
    mock_os.path.dirname.return_value = "/mock/tapo-320ws/recordings"

    response = client.delete("/tapo-320ws/recordings")

    assert response.status_code == 200
    assert response.json() == "Recording deletion successful"
    mock_os.remove.assert_not_called()
