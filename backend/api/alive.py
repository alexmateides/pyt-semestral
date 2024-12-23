from fastapi import APIRouter

# prefix /alive
router = APIRouter()


# Simple alive ping
@router.get("/")
async def get_alive():
    return {"message": "Alive!"}
