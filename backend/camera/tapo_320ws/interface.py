from backend.camera.base_interface import CameraBaseInterface
from backend.camera.tapo_320ws.utils import get_auth_by_name
from pytapo import Tapo


class Tapo320WSBaseInterface(CameraBaseInterface):
    """
    Interface class for TP-Link Tapo 320WS - outdoor Wi-Fi camera that I currently use
    This implementation uses pytapo library for camera API access
    """

    def __init__(self, name: str):
        self.name = name

        # get auth
        ip, username, password, camera_username, camera_password = get_auth_by_name(name)

        self.ip = ip
        self.username = username
        self.password = password
        self.camera_username = camera_username
        self.camera_password = camera_password

        super().__init__(ip, username, password)
        self.tapo_interface = Tapo(host=self.ip, user=self.username, password=self.password)

    def get_info(self) -> dict:
        """
        Returns: basic information about the Tapo camera
        """

        basic_info = self.tapo_interface.getBasicInfo()

        return basic_info

    def get_light_status(self) -> dict:
        """
        Gets the floodlight status

        Returns: floodlight status (on/off)
        """

        floodlight_status = self.tapo_interface.getWhitelampStatus()

        return floodlight_status

    def change_light_status(self) -> None:
        """
        Changes the floodlight status (on/off)

        Returns: None
        """

        self.tapo_interface.reverseWhitelampStatus()

        return None

    def get_stream_url(self) -> str:
        """
        Gets URL for camera stream

        Returns: stream URL
        """
        stream_url = f"rtsp://{self.camera_username}:{self.camera_password}@{self.ip}:554/stream2"

        return stream_url

    def get_night_vision_status(self) -> str:
        """
        Gets the night vision status

        Returns: Night vision status
        """
        night_vision_status = self.tapo_interface.getDayNightMode()

        return night_vision_status

    def change_night_vision_status(self) -> None:
        """
        Changes the night vision status (on/off)

        Returns: None
        """
        night_vision_status = self.tapo_interface.getDayNightMode()

        if night_vision_status == 'off' or night_vision_status == 'auto':
            self.tapo_interface.setDayNightMode('on')
            return None

        self.tapo_interface.setDayNightMode('off')

        return None
