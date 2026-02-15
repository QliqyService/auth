from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path
from starlette import status

from app.managers import Managers
from app.router.fastapi_users import fastapi_users
from app.schemas.auth import PerpetualTokenResponse
from app.schemas.users import UserCreate, UserRead


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Auth"],
)

# /login
# /logout
router.include_router(
    router=fastapi_users.get_auth_router(
        Managers.auth.authentication_backend,
        # requires_verification=True,
    ),
)


# /register
router.include_router(
    router=fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)

# /request-verify-token
# /verify
router.include_router(
    router=fastapi_users.get_verify_router(UserRead),
)

# /forgot-password
# /reset-password
router.include_router(
    router=fastapi_users.get_reset_password_router(),
)


@router.post(
    "/users/{user_id}/perpetual_token_generation",
    status_code=status.HTTP_200_OK,
    response_model=PerpetualTokenResponse,
)
async def perpetual_token_generation(
    user_id: Annotated[UUID, Path(title="User ID")],
):
    """
    Generate a perpetual token for the user.

    Args:
        user_id (UUID): ID of the user for whom to generate the token.

    Returns:
        PerpetualTokenResponse: Response containing the generated token.
    """
    return await Managers.auth.generate_perpetual_token(user_id=user_id)
