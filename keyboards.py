from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class Pagination(CallbackData, prefix='pag'):
    page: int
    action: str
    pref: str


def paginator(buttons: list[str], pref: str, page: int = 0):
    builder = InlineKeyboardBuilder()
    for button in buttons:
        if button == '◀ Пред':
            builder.add(InlineKeyboardButton(text=button, callback_data=Pagination(page=page, action=f'prev_{pref}',
                                                                                   pref=pref).pack()))
        elif button == 'След ▶':
            builder.add(InlineKeyboardButton(text=button, callback_data=Pagination(page=page, action=f'next_{pref}',
                                                                                   pref=pref).pack()))
        elif button == '+1':
            builder.add(InlineKeyboardButton(text=button, callback_data=Pagination(page=page, action='+1',
                                                                                   pref=pref).pack()))
        elif button == '-1':
            builder.add(InlineKeyboardButton(text=button, callback_data=Pagination(page=page, action='-1',
                                                                                   pref=pref).pack()))
        else:
            builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup()


def main_menu(buttons: list[str]):
    builder = InlineKeyboardBuilder()
    for button in buttons:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup()
