from fastapi import APIRouter
from backend.api.tapo_320ws.info import router as info_router
from backend.api.tapo_320ws.light import router as light_router

router = APIRouter()

router.include_router(info_router, tags=["Info"])
router.include_router(light_router, tags=["Light"])
