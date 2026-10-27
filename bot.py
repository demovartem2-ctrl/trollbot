import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatType

from mat import is_mat, make_reply

TOKEN = os.environ["BOT_TOKEN"]
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
    await m.reply(f"Здарова, {display_name(m)}. Матюкайся — отвечу 😈")

@dp.message(F.text)
async def on_text(m: Message):
    # Проверяем на мат
    if not is_mat(m.text or ""):
        return

    # В личке отвечаем на всё
    if m.chat.type == ChatType.PRIVATE:
        await m.reply(make_reply(display_name(m)))
        return

    # В группах/супергруппах
    if m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        
        # Проверяем: упомянули через @ или ответили на сообщение бота?
        is_mentioned = f"@{bot_username}" in (m.text or "")
        is_reply = m.reply_to_message and m.reply_to_message.from_user.id == bot_info.id

        if is_mentioned or is_reply:
            await m.reply(make_reply(display_name(m)))

# На всякий случай отвечаем на другие типы сообщений (стикеры, гифки) в личке
@dp.message(F.chat.type == ChatType.PRIVATE)
async def on_other(m: Message):
    if not m.text:
        await m.reply(f"{display_name(m)}, ты хуйню какую-то прислал, долбоёб, лучше бы матом написал 🤬")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
