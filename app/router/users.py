from fastapi import APIRouter

from app.router.fastapi_users import fastapi_users
from app.schemas.users import UserRead, UserUpdate


router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)

# /me
# /{id}
router.include_router(
    router=fastapi_users.get_users_router(
        UserRead,
        UserUpdate,
    ),
)
