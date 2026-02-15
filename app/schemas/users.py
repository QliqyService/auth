from fastapi_users import schemas
from pydantic import UUID4


class UserRead(schemas.BaseUser[UUID4]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    def create_update_dict(self):
        return schemas.model_dump(
            self,
            exclude_unset=True,
            exclude_none=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
            },
        )

    def create_update_dict_superuser(self):
        return schemas.model_dump(
            self,
            exclude_unset=True,
            exclude_none=True,
            exclude={"id"},
        )
