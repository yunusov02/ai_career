from fastapi import APIRouter

from app.api.routes.guide import router as guide_router
from app.api.routes.auth import router as auth_router
from app.api.routes.history import router as history_router


router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(guide_router, prefix="/guide", tags=["Public career guide"])
router.include_router(history_router, prefix="/history", tags=["User history"])
