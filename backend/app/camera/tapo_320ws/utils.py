"""
Utility function for Tapo320WS cameras
"""
from typing import Tuple, List
import sqlite3

from app.database.sqlite_interface import SqliteInterface


def get_auth_by_name(name: str) -> Tuple[str, str, str, str, str]:
    """
    Gets authorization for camera with name=name from SQL database
    Args:
        name: name of the camera

    Returns: Tuple[ip, username, password]
    """
    try:
        interface = SqliteInterface()
        interface.cursor.execute(
            """
            SELECT ip, username, password, camera_username, camera_password
            FROM cameras
            WHERE name = ?
            """,
            (name,)
        )
        row = interface.cursor.fetchone()

        return row[0], row[1], row[2], row[3], row[4]

    except sqlite3.Error as error:
        raise error
    except TypeError as type_error:
        raise type_error


def list_tapo_320ws_camera_names() -> List:
    """
    Returns: list of dicts containing camera info
    """
    try:
        interface = SqliteInterface()
        interface.cursor.execute(
            """
            SELECT * FROM cameras
            WHERE model="tapo_320ws"
            """
        )

        rows = interface.cursor.fetchall()

        result_names = []

        for row in rows:
            result_names.append(row[0])

        return result_names

    except sqlite3.Error as error:
        raise error
