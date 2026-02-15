from sqladmin import ModelView

from app.db.models import User


class UserAdminView(ModelView, model=User):
    can_delete = False
    can_edit = True
    can_create = False
    can_view_details = True

    column_list = [
        User.id,
        User.email,
        User.is_verified,
        User.is_active,
        User.is_superuser,
        User.created_at,
    ]
    column_searchable_list = [
        User.id,
        User.email,
    ]
    column_sortable_list = [
        User.is_active,
        User.is_verified,
        User.is_superuser,
        User.created_at,
    ]

    category = "Accounts"
    name = "User"
    name_plural = "Users"

    column_labels = {
        "is_verified": "Verified",
        "created_at": "Joined At",
        "hashed_password": "Password",
    }

    # async def on_model_change(self, data, model, is_created, request) -> None:
    #     if not is_created:
    #         if hashed_password := data.get("hashed_password"):
    #             async with Services.database.get_session() as session:
    #                 users_db = User.get_db(session=session)
    #                 user_manager = UserManager(users_db)
    #                 data["hashed_password"] = user_manager.password_helper.hash(hashed_password)
    #
    #     return await super().on_model_change(data, model, is_created, request)
