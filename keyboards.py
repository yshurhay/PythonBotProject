from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(buttons):
    builder = InlineKeyboardBuilder()
    for button in buttons:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup()
