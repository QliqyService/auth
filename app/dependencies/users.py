from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.db.models import User
from app.managers.users import UserManager
from app.services import Services


if TYPE_CHECKING:
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase


async def get_users_db():
    async with Services.database.session() as session:
        yield User.get_db(session=session)


async def get_user_manager(users_db: Annotated["SQLAlchemyUserDatabase", Depends(get_users_db)]):
    yield UserManager(users_db)
