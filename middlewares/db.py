from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from db.models import UserManager


class DatabaseMiddleware(BaseMiddleware):
    """
    A middleware which send user's information from db to handler
    """
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]):
        user_upd: User = data.get('event_from_user')
        if not user_upd:   # if an update not from user just skip query to db
            return await handler(event, data)

        # if not - get the user from db or create new
        usermanager: UserManager = data.get('usermanager')
        if not usermanager.get_user(user_id=user_upd.id):
            usermanager.add_user(
                user_id=user_upd.id,
                username=user_upd.username,
                first_name=user_upd.first_name,
                last_name=user_upd.last_name,
            )
        data['user'] = usermanager.get_user(user_id=user_upd.id)
        return await handler(event, data)

