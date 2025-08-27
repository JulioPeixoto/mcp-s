from fastapi import APIRouter

from .v1.health import router as health_router
from .v1.users import router as users_router

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(users_router)

__all__ = ["router"]
