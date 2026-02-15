from typing import TYPE_CHECKING

import sqlalchemy as sa
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase, SQLAlchemyBaseAccessTokenTableUUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import CreatedAtMixin, SQLAlchemyBase


if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AccessToken(SQLAlchemyBase, CreatedAtMixin, SQLAlchemyBaseAccessTokenTableUUID):
    __tablename__ = "access_tokens"

    user_id: Mapped[sa.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="cascade"),
        nullable=False,
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyAccessTokenDatabase(session, cls)
