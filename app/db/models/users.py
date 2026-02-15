from typing import TYPE_CHECKING, Any

import fastapi_users_db_sqlalchemy
import sqlalchemy as sa
from fastapi_users.models import UP

from app.db.models.base import CreatedAtMixin, SQLAlchemyBase


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SQLAlchemyUserDatabase(fastapi_users_db_sqlalchemy.SQLAlchemyUserDatabase):
    async def update(self, user: UP, update_dict: dict[str, Any]) -> UP:
        query = sa.update(User).where(User.id == user.id).values(**update_dict).returning(User)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar()


class User(SQLAlchemyBase, CreatedAtMixin, fastapi_users_db_sqlalchemy.SQLAlchemyBaseUserTableUUID):
    __tablename__ = "users"

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)
