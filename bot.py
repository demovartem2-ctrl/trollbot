import asyncio
import logging
import os
import time
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatType

from mat import is_mat, make_reply

# Берем токен из настроек Render
TOKEN = os.environ.get("BOT_TOKEN")
API_BASE = os.environ.get("API_BASE", "https://misugram.cloud-ip.cc")

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(api=TelegramAPIServer.from_base(API_BASE))
bot = Bot(TOKEN, session=session)
dp = Dispatcher()

# Защита от спама в чатах (chat_id: время последнего ответа)
chat_cooldowns = {}
COOLDOWN_TIME = 15  # Секунд между ответами в одном чате

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
    # Если это не мат — молчим (кроме лички, там можно отвечать на всё)
    if not is_mat(m.text or ""):
        # В личке если просто написали "привет", можно ответить
        if m.chat.type == ChatType.PRIVATE and "привет" in (m.text or "").lower():
            await m.reply(f"И тебе привет, {display_name(m)}. Матюкайся давай 🤬")
        return

    # --- ЛОГИКА ДЛЯ ЛИЧКИ ---
    if m.chat.type == ChatType.PRIVATE:
        await m.reply(make_reply(display_name(m)))
        return

    # --- ЛОГИКА ДЛЯ ГРУПП ---
    if m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        current_time = time.time()
        last_time = chat_cooldowns.get(m.chat.id, 0)
        
        # Проверяем, прошло ли 15 секунд с последнего ответа
        if current_time - last_time < COOLDOWN_TIME:
            return  # Если не прошло — молчим
            
        # Если прошло — отвечаем и запоминаем время
        chat_cooldowns[m.chat.id] = current_time
        await m.reply(make_reply(display_name(m)))

# Отвечаем на стикеры/фото в личке (чтобы бот не казался мертвым)
@dp.message(F.chat.type == ChatType.PRIVATE)
async def on_other(m: Message):
    if not m.text:
        await m.reply(f"{display_name(m)}, ты хуйню какую-то прислал, долбоёб, лучше бы матом написал 🤬")

async def main():
    logging.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
