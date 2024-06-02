from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from lexicon import LEXICON_KB_EN

buttons = [
    KeyboardButton(text=LEXICON_KB_EN["kb_upload"]),
    KeyboardButton(text=LEXICON_KB_EN["kb_check"]),
    KeyboardButton(text=LEXICON_KB_EN["kb_spend"]),
]

builder = ReplyKeyboardBuilder()
builder.row(*buttons, width=2)
main_kb_en = builder.as_markup(resize_keyboard=True)
