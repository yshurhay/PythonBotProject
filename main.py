import asyncio
import os

from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv

from handlers import router

load_dotenv(find_dotenv())

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
dp.include_router(router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
