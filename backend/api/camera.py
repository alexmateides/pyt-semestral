from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.database.sqlite_interface import SqliteInterface


# pydantic model for Camera
class Tapo320WSPydanticModel(BaseModel):
    name: str
    model: str
    ip: str
    username: str
    password: str
    camera_username: str
    camera_password: str


# prefix /camera
router = APIRouter()

# interface init
sqlite_interface = SqliteInterface()

# Ensure camera table exists
sqlite_interface.exec("""
CREATE TABLE IF NOT EXISTS cameras (
    name TEXT PRIMARY KEY,
    model TEXT NOT NULL,
    ip TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    camera_username TEXT NOT NULL,
    camera_password TEXT NOT NULL
)
""")


@router.get("/")
async def get_all_cameras() -> JSONResponse:
    """
    Returns: List of cameras
    """
    try:
        sqlite_interface.cursor.execute('SELECT * FROM cameras')
        cameras = sqlite_interface.cursor.fetchall()
        camera_list = [
            {
                "name": row[0],
                "model": row[1],
                "ip": row[2],
                "username": row[3],
                "password": row[4],
                "camera_username": row[5],
                "camera_password": row[6]
            }
            for row in cameras
        ]
        return JSONResponse(status_code=200, content=camera_list)
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error retrieving cameras: {error}")


@router.post("/")
async def add_or_update_camera(camera: Tapo320WSPydanticModel) -> JSONResponse:
    """
    If camera doesn't exist, it will be created.
    Else the params of the existing camera with the same name are updated.

    Args:
        camera: Camera parameters

    Returns:
    """
    try:
        # Check if the camera already exists
        sqlite_interface.cursor.execute('SELECT * FROM cameras WHERE name = ?', (camera.name,))
        existing_camera = sqlite_interface.cursor.fetchone()

        # Insert new camera
        if not existing_camera:
            sqlite_interface.cursor.execute("""
                INSERT INTO cameras (name, model, ip, username, password, camera_username, camera_password) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (camera.name, camera.model, camera.ip, camera.username, camera.password, camera.camera_username,
                  camera.camera_password))
            sqlite_interface.connection.commit()
            return JSONResponse(status_code=200, content={"response": f"Camera {camera.name} created successfully"})

        # Update existing camera
        else:
            sqlite_interface.cursor.execute("""
                UPDATE cameras
                SET model = ?, ip = ?, username = ?, password = ?, camera_username = ?, camera_password = ?
                WHERE name = ?
            """, (
                camera.model, camera.ip, camera.username, camera.password, camera.camera_username,
                camera.camera_password,
                camera.name))
            sqlite_interface.connection.commit()
            return JSONResponse(status_code=200, content={"response": f"Camera {camera.name} updated successfully"})

    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error adding or updating camera: {error}")


@router.delete("/")
async def delete_camera(name: str) -> JSONResponse:
    """
    Deletes a camera specified by name.

    Args:
        name: Name of the camera to delete

    Returns: None
    """
    try:
        sqlite_interface.cursor.execute('SELECT * FROM cameras WHERE name = ?', (name,))
        existing_camera = sqlite_interface.cursor.fetchone()

        if not existing_camera:
            raise HTTPException(status_code=404, detail=f"Camera {name} not found")

        sqlite_interface.cursor.execute('DELETE FROM cameras WHERE name = ?', (name,))
        sqlite_interface.connection.commit()

        return JSONResponse(status_code=200, content={"response": f"Camera {name} deleted successfully"})
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error deleting camera: {error}")


@router.get("/{name}")
async def get_camera_by_name(name: str) -> JSONResponse:
    """
    Get details of a camera by its name.

    Args:
        name: Name of the camera

    Returns: Camera details
    """
    try:
        sqlite_interface.cursor.execute('SELECT * FROM cameras WHERE name = ?', (name,))
        camera = sqlite_interface.cursor.fetchone()

        if not camera:
            raise HTTPException(status_code=404, detail=f"Camera {name} not found")

        return JSONResponse(status_code=200, content={
            "name": camera[0],
            "model": camera[1],
            "ip": camera[2],
            "username": camera[3],
            "password": camera[4],
            "camera_username": camera[5],
            "camera_password": camera[6]
        })
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Error retrieving camera: {error}")
