from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Quick start'),
        BotCommand(command='/rules',
                   description='Need to know'),
        BotCommand(command='/upload',
                   description='Send a car photo'),
        BotCommand(command='/balance',
                   description='Count of your scores'),
        BotCommand(command='/spend',
                   description='Exchange a score'),
        BotCommand(command='/see_all',
                   description='Check your uploaded images'),
    ]
    await bot.set_my_commands(main_menu_commands)
