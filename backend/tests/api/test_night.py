from unittest.mock import patch
from fastapi.exceptions import HTTPException


def test_get_night_success(client):
    response = client.get("/tapo-320ws/night/TestCam", headers={"api-key": "TEST"})

    assert response.status_code == 200
    assert response.json() == "off"


@patch("backend.api.tapo_320ws.night.Tapo320WSBaseInterface")
def test_get_night_fail(mock_camera_class, client):
    mock_camera_instance = mock_camera_class.return_value
    mock_camera_instance.get_night_vision_status.side_effect = HTTPException(status_code=404, detail="Not found")

    response = client.get("/tapo-320ws/night/TestCam2", headers={"api-key": "TEST"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}
    mock_camera_instance.get_night_vision_status.assert_called_once()


def test_post_night_success(client):
    response = client.post("/tapo-320ws/night/TestCam", headers={"api-key": "TEST"})

    assert response.status_code == 200
    # status didn't change since test values are fixed
    assert response.json() == "off"


@patch("backend.api.tapo_320ws.night.Tapo320WSBaseInterface")
def test_post_night_fail(mock_camera_class, client):
    mock_camera_instance = mock_camera_class.return_value

    mock_camera_instance.change_night_vision_status.side_effect = HTTPException(
        status_code=404,
        detail="An error occurred while changing the night status."
    )

    response = client.post("/tapo-320ws/night/TestCamFail", headers={"api-key": "TEST"})

    assert response.status_code == 404
    assert response.json() == {"detail": "An error occurred while changing the night status."}

    mock_camera_instance.change_night_vision_status.assert_called_once()

    mock_camera_instance.get_night_vision_status.assert_not_called()
