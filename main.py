import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from dotenv import find_dotenv, load_dotenv

from handlers import router
from parsing import get_food_data, get_about_data, get_delivery_data, get_payments_data
from info import buttons, info

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
dp.include_router(router)


async def main():
    buttons['О нас 💭']['caption'] = await get_about_data()
    buttons['Доставка 🚗']['caption'] = await get_delivery_data()
    buttons['Оплата 💸']['caption'] = await get_payments_data()
    info['pizza_captions'] = await get_food_data('https://pizza-italia.by/catalog/pitstsa/')
    info['rolotto_captions'] = await get_food_data('https://pizza-italia.by/catalog/rolly/')
    info['drink_captions'] = await get_food_data('https://pizza-italia.by/catalog/kholodnye-napitki/')
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(commands=[BotCommand(command='menu', description='show menu'),
                                        BotCommand(command='start', description='show menu')])
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
