from backend.camera.tapo_320ws.interface import Tapo320WSBaseInterface


def test_get_info():
    interface = Tapo320WSBaseInterface("TestCam")
    info = interface.get_info()
    assert info["device_info"]["basic_info"] == {
        "device_type": "SMART.IPCAMERA",
        "device_info": "C320WS 2.0 IPC",
        "features": 3,
        "device_model": "C320WS",
        "sw_version": "1.2.1 Build",
        "device_name": "C320WS 2.0",
        "hw_version": "1.0",
        "device_alias": "TestCam",
        "mac": "D8-DE-44-41-5F-DE",
        "manufacturer_name": "TP-LINK",
    }


def test_change_light_status():
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.change_light_status() is None


def test_change_night_vision_light_status():
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.change_night_vision_status() is None


def test_get_light_status():
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.get_light_status() == {
        "status": 0,
        "rest_time": 0
    }


def test_get_night_vision_status():
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.get_night_vision_status() == "off"


def test_get_stream_url():
    interface = Tapo320WSBaseInterface("TestCam")
    stream_url = interface.get_stream_url()
    assert stream_url == "rtsp://admin:admin@192.168.0.123:554/stream1"


def test_get_time_correction():
    interface = Tapo320WSBaseInterface("TestCam")
    assert interface.get_time_correction() == 0


def test_get_recordings():
    interface = Tapo320WSBaseInterface("TestCam")
    recordings = interface.get_recordings("2024-12-26")
    assert len(recordings) == 2
    assert recordings == [
        {
            "startTime": "15:47:43",
            "endTime": "15:48:50",
            "vedio_type": 2,
            "duration_seconds": 67,
            "date": "2024-12-26",
            "id": "search_video_results_1"
        },
        {
            "startTime": "16:02:55",
            "endTime": "16:04:07",
            "vedio_type": 2,
            "duration_seconds": 72,
            "date": "2024-12-26",
            "id": "search_video_results_2"
        }
    ]


def test_get_events():
    interface = Tapo320WSBaseInterface("TestCam")
    events = interface.get_events()
    assert len(events) == 1
    assert events == [
        {
            "start_time": 1735342234,
            "end_time": 1735342240,
            "alarm_type": 6,
            "startRelative": 10,
            "endRelative": 4
        }
    ]
