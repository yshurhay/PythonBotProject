from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.filters import CommandStart, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import keyboards as kb
from info import buttons, info

router = Router()


class Order(StatesGroup):
    name = State()
    number = State()
    address = State()
    payment = State()


@router.message(CommandStart())
async def start_cmd(message: Message):
    """Event to /start cmd"""

    user_id = message.from_user.id
    info['item_captions'][user_id] = []
    info['final_price'][user_id] = 0
    info['category'] = 'Главное меню'
    data = buttons[info['category']]

    await message.answer_photo(photo=data['photo'],
                               caption=data['caption'], reply_markup=kb.main_menu(buttons=data['buttons']))


@router.callback_query(kb.Pagination.filter(F.action.in_(['+1', '-1'])))
async def count_handler(callback: CallbackQuery, callback_data: kb.Pagination):
    """Create callback event to +/- item count in the cart"""

    await callback.answer()

    page = int(callback_data.page)
    pref = callback_data.pref
    user_id = callback.from_user.id

    if callback_data.action == '+1':
        info['item_captions'][user_id][page]['count'] += 1
        info['final_price'][user_id] += float(info['item_captions'][user_id][page]['price'])

    elif callback_data.action == '-1':
        info['item_captions'][user_id][page]['count'] -= 1
        info['final_price'][user_id] -= float(info['item_captions'][user_id][page]['price'])

        if info['item_captions'][user_id][page]['count'] == 0:
            await callback.answer('Товар удалён')
            info['item_captions'][user_id].remove(info['item_captions'][user_id][page])
            page -= 1

    if info['item_captions'][user_id]:
        data = buttons[info['category']]
        photo_url = info[f'{pref}_captions'][user_id][page]['photo']
        caption = (f'{info['item_captions'][user_id][page]['name']}\n'
                   f'{info['item_captions'][user_id][page]['mass']}\n'
                   f'{info['item_captions'][user_id][page]['count']} х {info['item_captions'][user_id][page]['price']} руб.\n\n'
                   f'Итого: {info['final_price'][user_id]:.2f} руб.')

        await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                          reply_markup=kb.paginator(buttons=data['buttons'], pref=pref, page=page))

    else:
        info['category'] = 'Пустая корзина'
        data = buttons[info['category']]
        await callback.message.edit_media(media=InputMediaPhoto(media=data['photo'], caption=data['caption']),
                                          reply_markup=kb.main_menu(buttons=data['buttons']))


@router.callback_query(kb.Pagination.filter(F.action.in_(['prev_item', 'next_item'])))
async def pagination_handler(callback: CallbackQuery, callback_data: kb.Pagination):
    """Create event prev/next to change item"""

    await callback.answer()

    page_num = int(callback_data.page)
    pref = callback_data.pref
    user_id = callback.from_user.id

    if not len(info[f'item_captions'][user_id]) == 1:
        if callback_data.action == 'next_item':
            page = (page_num + 1) % len(info[f'item_captions'][user_id])
        else:
            page = (page_num - 1) % len(info[f'item_captions'][user_id]) if page_num > 0 else len(info[f'{pref}_captions'][user_id]) - 1

        photo_url = info[f'item_captions'][user_id][page]['photo']
        data = buttons[info['category']]
        info['current_item'] = info[f'item_captions'][user_id][page]
        caption = (f'{info['item_captions'][user_id][page]['name']}\n'
                   f'{info['item_captions'][user_id][page]['mass']}\n'
                   f'{info['item_captions'][user_id][page]['count']} х {info['item_captions'][user_id][page]['price']} руб.\n\n'
                   f'Итого: {info['final_price'][user_id]:.2f} руб.')

        await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                          reply_markup=kb.paginator(buttons=data['buttons'], pref=pref, page=page))


@router.callback_query(kb.Pagination.filter(F.action))
async def pagination_handler(callback: CallbackQuery, callback_data: kb.Pagination):
    """Create event prev/next to change item in food"""

    await callback.answer()

    page_num = int(callback_data.page)
    pref = callback_data.pref

    if not len(info[f'{pref}_captions']) == 1:
        if callback_data.action == f'next_{pref}':
            page = (page_num + 1) % len(info[f'{pref}_captions'])
        else:
            page = (page_num - 1) % len(info[f'{pref}_captions']) if page_num > 0 else len(info[f'{pref}_captions']) - 1

        photo_url = info[f'{pref}_captions'][page]['photo']
        data = buttons[info['category']]
        info['current_item'] = info[f'{pref}_captions'][page]
        caption = (f'{info[f'{pref}_captions'][page]['name']}\n'
                   f'{info[f'{pref}_captions'][page]['mass']}\n'
                   f'{info[f'{pref}_captions'][page]['price']} руб.')

        await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                          reply_markup=kb.paginator(buttons=data['buttons'], pref=pref, page=page))


@router.callback_query(F.data == 'Заказать')
async def order_food(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(Order.name)
    await callback.message.answer('Введите ваше имя', reply_markup=kb.name_kb(callback.from_user.first_name))


@router.message(Order.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Order.number)
    await message.answer('Введите ваш номер', reply_markup=kb.contact_kb)


@router.message(Order.number)
async def number(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(number=message.text)
    else:
        await state.update_data(number=f'+{message.contact.phone_number}')
    await state.set_state(Order.address)
    await message.answer('Введите адрес', reply_markup=ReplyKeyboardRemove())


@router.message(Order.address)
async def address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(Order.payment)
    await message.answer('Как будете оплачивать?', reply_markup=kb.payment_kb)


@router.message(Order.payment)
async def payment(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(payment=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    text = ''
    for item in info['item_captions'][user_id]:
        text += f'{item['name']}\n'
        text += f'{item['count']} x {item['price']} руб.\n'
    order = (f'Заказ:\n\n'
             f'Имя: {data['name']}\n'
             f'Номер: {data['number']}\n'
             f'Адрес: {data['address']}\n'
             f'Оплата: {data['payment']}\n\n'
             f'{text}\n'
             f'Итого: {info['final_price'][user_id]} руб.')
    await message.answer('Ваш заказ принят', reply_markup=ReplyKeyboardRemove())
    await bot.send_message(chat_id='689120290', text=order)


@router.callback_query(F.data == 'Купить')
async def add_to_cart(callback: CallbackQuery):
    """Add item to the cart and notify about it"""

    user_id = callback.from_user.id

    if info['current_item'] in info['item_captions'][user_id]:
        await callback.answer('Товар уже в корзине')

    else:
        await callback.answer('Добавлено в корзину')
        info['final_price'][user_id] += float(info['current_item']['price'])
        info['current_item']['count'] = 1
        info['item_captions'][user_id].append(info['current_item'])


@router.callback_query(or_f(F.data == 'Назад', F.data == 'На главную'))
async def back(callback: CallbackQuery):
    """Create 'back' events and create 'old' buttons"""

    await callback.answer()

    if info['category'] in ('Пицца', 'Ролотто', 'Напитки'):
        info['category'] = 'Товары'
    else:
        info['category'] = 'Главное меню'

    data = buttons[info['category']]

    await callback.message.edit_media(media=InputMediaPhoto(media=data['photo'], caption=data['caption']),
                                      reply_markup=kb.main_menu(buttons=data['buttons']))


@router.callback_query(F.data == 'Корзина')
async def callback_food(callback: CallbackQuery):
    """Create buttons and cart information"""

    await callback.answer()

    user_id = callback.from_user.id

    if info['item_captions'][user_id]:

        pref = 'item'
        info['current_item'] = info['item_captions'][user_id][0]
        category = callback.data
        info['category'] = category
        data = buttons[info['category']]
        photo_url = info[f'{pref}_captions'][user_id][0]['photo']
        caption = (f'{info['item_captions'][user_id][0]['name']}\n'
                   f'{info['item_captions'][user_id][0]['mass']}\n'
                   f'{info['item_captions'][user_id][0]['count']} х {info['item_captions'][user_id][0]['price']} руб.\n\n'
                   f'Итого: {info['final_price'][user_id]:.2f} руб.')

        await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                          reply_markup=kb.paginator(buttons=data['buttons'], pref=pref))

    else:

        info['category'] = 'Пустая корзина'
        data = buttons[info['category']]

        await callback.message.edit_media(media=InputMediaPhoto(media=data['photo'], caption=data['caption']),
                                          reply_markup=kb.main_menu(buttons=data['buttons']))


@router.callback_query(or_f(F.data == 'Пицца', F.data == 'Ролотто', F.data == 'Напитки'))
async def callback_food(callback: CallbackQuery):
    """Create buttons with food information"""

    await callback.answer()

    pref = ''

    if callback.data == 'Пицца':
        pref = 'pizza'
    elif callback.data == 'Ролотто':
        pref = 'rolotto'
    elif callback.data == 'Напитки':
        pref = 'drink'

    info['current_item'] = info[f'{pref}_captions'][0]
    category = callback.data
    info['category'] = category
    data = buttons[info['category']]
    photo_url = info[f'{pref}_captions'][0]['photo']
    caption = (f'{info[f'{pref}_captions'][0]['name']}\n'
               f'{info[f'{pref}_captions'][0]['mass']}\n'
               f'{info[f'{pref}_captions'][0]['price']} руб.')

    await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                      reply_markup=kb.paginator(buttons=data['buttons'], pref=pref))


@router.callback_query(F.data)
async def callback_data_handler(callback: CallbackQuery):
    """Create simple buttons"""

    await callback.answer()

    category = callback.data
    info['category'] = category
    data = buttons[info['category']]

    await callback.message.edit_media(media=InputMediaPhoto(media=data['photo'], caption=data['caption']),
                                      reply_markup=kb.main_menu(buttons=data['buttons']))



