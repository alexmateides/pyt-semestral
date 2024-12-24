from backend.camera.base_interface import CameraBaseInterface
from pytapo import Tapo


class Tapo320WSBaseInterface(CameraBaseInterface):
    """
    Interface class for TP-Link Tapo 320WS - outdoor Wi-Fi camera that I currently use
    This implementation uses pytapo library for camera API access
    """

    def __init__(self, ip: str, username: str, password: str):
        super().__init__(ip, username, password)
        self.tapo_interface = Tapo(host=self.ip, user=self.username, password=self.password)

    def get_info(self) -> dict:
        """

        Returns: basic information about the Tapo camera

        """

        basic_info = self.tapo_interface.getBasicInfo()

        return basic_info
