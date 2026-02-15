from sqladmin import ModelView

from app.db.models import AccessToken


class AccessTokenAdminView(ModelView, model=AccessToken):
    can_delete = True
    can_edit = False
    can_create = False
    can_view_details = True

    form_create_rules = ["user_id"]

    column_list = [
        AccessToken.user_id,
        AccessToken.token,
        AccessToken.created_at,
    ]
    column_searchable_list = [
        AccessToken.user_id,
        AccessToken.token,
    ]
    column_sortable_list = [
        AccessToken.created_at,
    ]

    category = "Accounts"
    name = "Access Token"
    name_plural = "Access Tokens"
