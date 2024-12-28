"""
API routing hub for /tapo-320ws endpoint
"""
from fastapi import APIRouter
from app.api.tapo_320ws.info import router as info_router
from app.api.tapo_320ws.light import router as light_router
from app.api.tapo_320ws.stream import router as stream_router
from app.api.tapo_320ws.night import router as night_router
from app.api.tapo_320ws.recordings import router as recordings_router

router = APIRouter()

router.include_router(info_router, tags=["Info"])
router.include_router(light_router, tags=["Light"])
router.include_router(stream_router, tags=["Stream"])
router.include_router(night_router, tags=["Night"])
router.include_router(recordings_router, tags=["Recordings"])
