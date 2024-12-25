from backend.database.sqlite_interface import SqliteInterface
from typing import Tuple


def get_auth_by_name(name: str) -> Tuple[str, str, str]:
    """
    Gets authorization for camera with name=name from SQL database
    Args:
        name: name of the camera

    Returns: Tuple[ip, username, password]
    """
    interface = SqliteInterface()
    interface.cursor.execute(
        f"""
        SELECT ip, username, password
        FROM cameras
        WHERE name = ?
        """,
        (name,)
    )
    camera = interface.cursor.fetchone()

    return camera[0], camera[1], camera[2]
