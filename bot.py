import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message

from mat import is_mat, make_reply

TOKEN = os.environ["BOT_TOKEN"]                     # 1780243347:...
API_BASE = os.environ.get("API_BASE", "https://misugram.cloud-ip.cc")

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(api=TelegramAPIServer.from_base(API_BASE))
bot = Bot(TOKEN, session=session)
dp = Dispatcher()


def display_name(m: Message) -> str:
    u = m.from_user
    if u is None:
        return "друг"
    return u.username and f"@{u.username}" or u.first_name or "друг"


@dp.message(CommandStart())
async def cmd_start(m: Message):
    await m.answer(
        f"Здарова, {display_name(m)}. Пиши — отвечу как надо 😈\n"
        "Матюкнешься — получишь в ответ в три раза хуже."
    )


@dp.message(F.text)
async def on_text(m: Message):
    if is_mat(m.text or ""):
        await m.reply(make_reply(display_name(m)))


@dp.message()
async def on_other(m: Message):
    # стикеры, фото и т.п. — тоже можем подколоть
    await m.reply(
        f"{display_name(m)}, ты хуйню какую-то прислал, долбоёб, "
        f"лучше бы матом написал 🤬"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
