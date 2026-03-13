from fastapi import APIRouter

from app.router.auth import router as auth_router
from app.router.shared import router as shared_router
from app.router.users import router as users_router


api_router = APIRouter()
api_router.include_router(shared_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
