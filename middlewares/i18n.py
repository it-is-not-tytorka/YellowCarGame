from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User


class TranslatorMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]):
        user: User = data.get('event_from_user')
        if not user:   # if an update not from user just skip query to db
            return await handler(event, data)

        # if not - get user's language from Telegram service and send this to handler
        user_lang = user.language_code
        translations = data.get('_translations')
        i18n = translations.get(user_lang)
        if not i18n:
            data['i18n'] = translations[translations['default']]
        else:
            data['i18n'] = i18n
        return await handler(event, data)
