from unittest.mock import patch
from fastapi.exceptions import HTTPException


def test_get_light_success(client):
    response = client.get("/tapo-320ws/light/TestCam", headers={"api-key": "TEST"})

    assert response.status_code == 200
    assert response.json() == {"status": 0, "rest_time": 0}


# simulate not found
@patch("backend.api.tapo_320ws.light.Tapo320WSBaseInterface")
def test_get_light_fail(mock_camera_class, client):
    mock_camera_instance = mock_camera_class.return_value
    mock_camera_instance.get_light_status.side_effect = HTTPException(status_code=404, detail="Not found")

    response = client.get("/tapo-320ws/light/TestCam2", headers={"api-key": "TEST"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found"}
    mock_camera_instance.get_light_status.assert_called_once()


def test_post_light_success(client):
    response = client.post("/tapo-320ws/light/TestCam", headers={"api-key": "TEST"})

    # actual light status didn't change since the test values are fixed
    assert response.status_code == 200
    assert response.json() == {"status": 0, "rest_time": 0}


@patch("backend.api.tapo_320ws.light.Tapo320WSBaseInterface")
def test_post_light_fail(mock_camera_class, client):
    mock_camera_instance = mock_camera_class.return_value

    mock_camera_instance.change_light_status.side_effect = HTTPException(
        status_code=404,
        detail="An error occurred while changing the light status."
    )

    response = client.post("/tapo-320ws/light/TestCamFail", headers={"api-key": "TEST"})

    assert response.status_code == 404
    assert response.json() == {"detail": "An error occurred while changing the light status."}

    mock_camera_instance.change_light_status.assert_called_once()

    mock_camera_instance.get_light_status.assert_not_called()
