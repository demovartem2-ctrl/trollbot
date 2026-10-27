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
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from mat import is_mat, make_reply

TOKEN = os.environ.get("BOT_TOKEN")
API_BASE = os.environ.get("API_BASE", "https://misugram.cloud-ip.cc")

# Render сам подставляет сюда адрес твоего сайта (например https://mybot.onrender.com)
WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_URL", "https://твой-сайт.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 8080))

logging.basicConfig(level=logging.INFO)

session = AiohttpSession(api=TelegramAPIServer.from_base(API_BASE))
bot = Bot(TOKEN, session=session)
dp = Dispatcher()

chat_cooldowns = {}
COOLDOWN_TIME = 15

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
    if not is_mat(m.text or ""):
        return

    if m.chat.type == ChatType.PRIVATE:
        await m.reply(make_reply(display_name(m)))
        return

    if m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        current_time = time.time()
        last_time = chat_cooldowns.get(m.chat.id, 0)
        
        if current_time - last_time < COOLDOWN_TIME:
            return 
            
        chat_cooldowns[m.chat.id] = current_time
        await m.reply(make_reply(display_name(m)))

@dp.message(F.chat.type == ChatType.PRIVATE)
async def on_other(m: Message):
    if not m.text:
        await m.reply(f"{display_name(m)}, ты хуйню какую-то прислал, долбоёб, лучше бы матом написал 🤬")

async def on_startup(bot: Bot):
    logging.info(f"Устанавливаю Webhook на {WEBHOOK_URL}")
    # drop_pending_updates=True нужен, чтобы Telegram не присылал старые сообщения
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)

def main():
    dp.startup.register(on_startup)
    app = web.Application()
    
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    logging.info(f"Запуск веб-сервера на порту {PORT}")
    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
