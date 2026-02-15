import asyncio

from loguru import logger as LOGGER

from app.db.models import User
from app.managers.users import UserManager
from app.services import Services


class FixtureManager:
    def __init__(self):
        self.default_password = "testtest"

        self.default_users = [
            {
                "id": "6f3e423c-0938-455f-abae-5f46cfc97970",
                "email": "support@qliqy.io",
                "is_active": True,
                "is_superuser": True,
                "is_verified": True,
            }
        ]

    async def create_users(self):
        LOGGER.info("Creating users...")

        async with Services.database.session() as session:
            users_db = User.get_db(session=session)
            users_manager = UserManager(users_db)

            default_hashed_password = users_manager.password_helper.hash(self.default_password)

            for user_created_dict in self.default_users:
                exists_user = await users_db.get(id=user_created_dict["id"])
                if exists_user:
                    LOGGER.info(f"> User {user_created_dict['email']} already exists")
                else:
                    user_created_dict["hashed_password"] = default_hashed_password
                    await users_db.create(create_dict=user_created_dict)
                    LOGGER.info(f"> User {user_created_dict['email']} created")

    async def upload_data(self):
        LOGGER.info("Uploading data...")
        await self.create_users()
        LOGGER.info("Uploading data... finished")


def main():
    app = FixtureManager()
    asyncio.run(Services.database.connect())
    asyncio.run(app.upload_data())
