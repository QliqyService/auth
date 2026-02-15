from app.db.models import AccessToken
from app.services import Services


async def get_access_tokens_db():
    async with Services.database.session() as session:
        yield AccessToken.get_db(session=session)
