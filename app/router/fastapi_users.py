import uuid

from fastapi_users import FastAPIUsers

from app.db.models import User
from app.dependencies import get_user_manager
from app.managers import Managers


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager=get_user_manager, auth_backends=[Managers.auth.authentication_backend]
)

current_active_user = fastapi_users.current_user(active=True)
current_active_superuser = fastapi_users.current_user(active=True, superuser=True)
