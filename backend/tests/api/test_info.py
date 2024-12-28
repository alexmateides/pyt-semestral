def test_get_info_success(client):

    response = client.get("/tapo-320ws/info/TestCam", headers={"api-key": "TEST"})

    assert response.status_code == 200
    camera_info = response.json()['device_info']['basic_info']
    assert camera_info['device_model'] == 'C320WS'
    assert camera_info['device_alias'] == 'TestCam'
