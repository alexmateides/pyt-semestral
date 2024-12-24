from fastapi import APIRouter
from backend.api.tapo_320ws.info import router as info_router

router = APIRouter()

router.include_router(info_router, tags=["Info"])
