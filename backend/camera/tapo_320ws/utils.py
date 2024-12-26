from backend.database.sqlite_interface import SqliteInterface
from typing import Tuple


def get_auth_by_name(name: str) -> Tuple[str, str, str, str, str]:
    """
    Gets authorization for camera with name=name from SQL database
    Args:
        name: name of the camera

    Returns: Tuple[ip, username, password]
    """
    interface = SqliteInterface()
    interface.cursor.execute(
        f"""
        SELECT ip, username, password, camera_username, camera_password
        FROM cameras
        WHERE name = ?
        """,
        (name,)
    )
    row = interface.cursor.fetchone()

    return row[0], row[1], row[2], row[3], row[4]
