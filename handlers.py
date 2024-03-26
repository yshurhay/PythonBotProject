from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, or_f
import keyboards as kb
from info import buttons, info

router = Router()


@router.message(CommandStart())
async def start_cmd(message: Message):
    info['category'] = 'Главное меню'
    data = buttons[info['category']]
    await message.answer_photo(photo=data['photo'],
                               caption=data['caption'], reply_markup=kb.main_menu(buttons=data['buttons']))


@router.callback_query(or_f(F.data == 'Назад', F.data == 'На главную'))
async def back(callback: CallbackQuery):
    await callback.answer()

    if info['category'] in ('Товары', 'О нас', 'Оплата', 'Доставка', 'Корзина', 'Пустая корзина'):
        info['category'] = 'Главное меню'
    else:
        info['category'] = 'Товары'

    data = buttons[info['category']]
    await callback.message.edit_media(media=InputMediaPhoto(media=data['photo'], caption=data['caption']),
                                      reply_markup=kb.main_menu(buttons=data['buttons']))


@router.callback_query(F.data == 'Купить')
async def add_to_cart(callback: CallbackQuery):
    if info['current_item'] in info['item_captions']:
        await callback.answer('Товар уже в корзине')
    else:
        await callback.answer('Добавлено в корзину')
        info['final_price'] += float(info['current_item']['price'])
        info['current_item']['count'] = 1
        info['item_captions'].append(info['current_item'])


@router.callback_query(F.data == 'Корзина')
async def callback_food(callback: CallbackQuery):
    await callback.answer()
    pref = 'item'

    if info['item_captions']:
        info['current_item'] = info['item_captions'][0]
        category = callback.data
        info['category'] = category
        data = buttons[info['category']]
        caption = (f'{info['item_captions'][0]['name']}\n'
                   f'{info['item_captions'][0]['mass']}\n'
                   f'{info['item_captions'][0]['count']} х {info['item_captions'][0]['price']} руб.\n\n'
                   f'Итого: {info['final_price']:.2f} руб.')
        photo_url = info[f'{pref}_captions'][0]['photo']

        await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                          reply_markup=kb.paginator(buttons=data['buttons'], pref=pref))

    else:
        info['category'] = 'Пустая корзина'
        data = buttons[info['category']]
        await callback.message.edit_media(media=InputMediaPhoto(media=data['photo'], caption=data['caption']),
                                          reply_markup=kb.main_menu(buttons=data['buttons']))


@router.callback_query(or_f(F.data == 'Пицца', F.data == 'Ролотто', F.data == 'Напитки'))
async def callback_food(callback: CallbackQuery):
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
    caption = '\n'.join(info[f'{pref}_captions'][0][text] for text in info[f'{pref}_captions'][0] if text != 'photo')
    photo_url = info[f'{pref}_captions'][0]['photo']

    await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                      reply_markup=kb.paginator(buttons=data['buttons'], pref=pref))


@router.callback_query(kb.Pagination.filter(F.action))
async def pagination_handler(callback: CallbackQuery, callback_data: kb.Pagination):
    page_num = int(callback_data.page)
    pref = callback_data.pref
    print(info['current_item'])

    if not len(info[f'{pref}_captions']) == 1:
        if callback_data.action == f'next_{pref}':
            page = (page_num + 1) % len(info[f'{pref}_captions'])
        else:
            page = (page_num - 1) % len(info[f'{pref}_captions']) if page_num > 0 else len(info[f'{pref}_captions']) - 1

        if pref == 'item':
            caption = (f'{info['item_captions'][page]['name']}\n'
                       f'{info['item_captions'][page]['mass']}\n'
                       f'{info['item_captions'][page]['count']} х {info['item_captions'][page]['price']} руб.\n\n'
                       f'Итого: {info['final_price']:.2f} руб.')
        else:
            caption = '\n'.join(f'{info[f'{pref}_captions'][page][text]}' for text in info[f'{pref}_captions'][page] if text != 'photo')
        photo_url = info[f'{pref}_captions'][page]['photo']
        data = buttons[info['category']]
        info['current_item'] = info[f'{pref}_captions'][page]

        await callback.answer()
        await callback.message.edit_media(media=InputMediaPhoto(media=photo_url, caption=caption),
                                          reply_markup=kb.paginator(buttons=data['buttons'], pref=pref, page=page))


@router.callback_query(F.data)
async def callback_data_handler(callback: CallbackQuery):
    category = callback.data
    info['category'] = category
    data = buttons[info['category']]
    await callback.answer()
    await callback.message.edit_media(media=InputMediaPhoto(media=data['photo'], caption=data['caption']),
                                      reply_markup=kb.main_menu(buttons=data['buttons']))



