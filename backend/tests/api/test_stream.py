def test_get_stream_url_success(client):
    response = client.get(f"/tapo-320ws/stream/TestCam")

    assert response.status_code == 200
    assert response.json() == {"streamUrl": "ws://localhost:8000/tapo-320ws/stream/ws/TestCam"}


def test_get_websocket(client):
    websocket = client.websocket_connect("/stream/ws/TestCam")

    assert websocket is not None
