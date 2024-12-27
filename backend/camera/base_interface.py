"""
Base camera interface for potential new camera models
"""
from abc import ABC, abstractmethod


class CameraBaseInterface(ABC):
    """
    Abstract class template for camera interfaces
    """

    @abstractmethod
    def __init__(self, ip: str, username: str, password: str) -> None:
        """

        Args:
            ip:         ip of the camera (ex. 192.168.1.123)
            username:   username for camera access (ex. admin)
            password:   password for camera access (ex. admin)
        """
        self.ip = ip
        self.username = username
        self.password = password

    @abstractmethod
    def get_info(self) -> dict:
        """
        Returns: basic camera info (ex. model_name, runtime ...)
        """

    def get_capabilities(self) -> dict:
        """
        Returns: basic camera capabilities
        """
