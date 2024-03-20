from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, or_f
import keyboards as kb
from info import info, level

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):
    level['category'] = 'Главное меню'
    data = info[level['category']]
    await message.answer_photo(photo='https://ibb.co/pZg1Fn0',
                               caption=data[0], reply_markup=kb.main_menu(buttons=data[1]))


@router.callback_query(or_f(F.data == 'Назад', F.data == 'На главную'))
async def back(callback: CallbackQuery):
    await callback.answer()

    if level['category'] in ('Товары', 'О нас', 'Оплата', 'Доставка', 'Корзина'):
        level['category'] = 'Главное меню'
    else:
        level['category'] = 'Товары'

    data = info[level['category']]
    await callback.message.edit_caption(caption=data[0], reply_markup=kb.main_menu(buttons=data[1]))


@router.callback_query(F.data)
async def callback_data(callback: CallbackQuery):
    category = callback.data
    level['category'] = category
    data = info[level['category']]
    await callback.answer()
    await callback.message.edit_caption(caption=data[0], reply_markup=kb.main_menu(buttons=data[1]))



