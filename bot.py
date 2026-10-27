import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.enums import ChatType
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from mat import make_reply

TOKEN = os.environ.get("BOT_TOKEN")
API_BASE = os.environ.get("API_BASE", "https://misugram.cloud-ip.cc")

WEBHOOK_HOST = os.environ.get("RENDER_EXTERNAL_URL", "https://твой-сайт.onrender.com")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 8080))

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
    await m.reply(f"Здарова, {display_name(m)}. Я буду ебашить на каждое твое сообщение 😈")

@dp.message(F.text)
async def on_text(m: Message):
    # Не отвечаем другим ботам
    if m.from_user and m.from_user.is_bot:
        return

    # В личке и в чатах отвечаем на любое сообщение
    await m.reply(make_reply(display_name(m)))

async def on_startup(bot: Bot):
    logging.info(f"Устанавливаю Webhook на {WEBHOOK_URL}")
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
