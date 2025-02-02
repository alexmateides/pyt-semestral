"""
tests for /tapo-320ws/night/{name} endpoints
"""
from unittest.mock import patch
from fastapi.exceptions import HTTPException


def test_get_night_success(client):
    """
    tests GET /tapo-320ws/night/{name}
    """
    response = client.get("/tapo-320ws/night/TestCam", headers={"api-key": "TEST"})

    assert response.status_code == 200
    assert response.json() == {'status': 0}


@patch("app.api.tapo_320ws.night.Tapo320WSBaseInterface")
def test_get_night_fail(mock_camera_class, client):
    """
    tests GET /tapo-320ws/night/{name} failure
    """
    mock_camera_instance = mock_camera_class.return_value
    mock_camera_instance.get_night_vision_status.side_effect = HTTPException(status_code=404, detail="Not found")

    response = client.get("/tapo-320ws/night/TestCam2", headers={"api-key": "TEST"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}
    mock_camera_instance.get_night_vision_status.assert_called_once()


def test_post_night_success(client):
    """
    tests POST /tapo-320ws/night/{name}
    """
    response = client.post("/tapo-320ws/night/TestCam", headers={"api-key": "TEST"})

    assert response.status_code == 200
    assert response.json() == {'status': 1}


@patch("app.api.tapo_320ws.night.Tapo320WSBaseInterface")
def test_post_night_fail(mock_camera_class, client):
    """
    tests POST /tapo-320ws/night/{name} failure
    """
    mock_camera_instance = mock_camera_class.return_value

    mock_camera_instance.change_night_vision_status.side_effect = HTTPException(
        status_code=404,
        detail="An error occurred while changing the night status."
    )

    response = client.post("/tapo-320ws/night/TestCamFail", headers={"api-key": "TEST"})

    assert response.status_code == 404
    assert response.json() == {"detail": "An error occurred while changing the night status."}

    mock_camera_instance.change_night_vision_status.assert_called_once()

    mock_camera_instance.get_night_vision_status.assert_called_once()
