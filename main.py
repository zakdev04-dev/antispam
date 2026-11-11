import asyncio
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db
from handlers import register_all_handlers
from services.penalty import penalty_background_worker

# Loglarni sozlash
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main")

# Render.com uchun oddiy Health Check veb-server
async def health_check(request):
    return web.Response(text="OK - Anti Spam Bot is running!", status=200)

async def start_web_server(port: int):
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info(f"Render Web Server 0.0.0.0:{port} portida ishga tushdi.")
    return runner

async def on_startup(bot: Bot):
    logger.info("MongoDB ma'lumotlar bazasiga ulanish...")
    await db.init_db()
    logger.info("MongoDB ulanishi muvaffaqiyatli amalga oshirildi!")

    bot_info = await bot.get_me()
    logger.info(f"Bot muvaffaqiyatli ishga tushdi: @{bot_info.username} (ID: {bot_info.id})")

async def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN ko'rsatilmagan! Iltimos, .env faylini tekshiring.")
        return

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Barcha handlerlarni ulash
    register_all_handlers(dp)

    # Render.com portini tinglash (Health check)
    web_runner = None
    try:
        web_runner = await start_web_server(config.PORT)
    except Exception as e:
        logger.warning(f"Web serverni ishga tushirishda ogohlantirish: {e}")

    # Startup hodisasi
    await on_startup(bot)

    # Orqa fon jarimalar tekshiruvchisini ishga tushirish (har 1 soatda)
    penalty_task = asyncio.create_task(penalty_background_worker(bot, interval_seconds=3600))

    try:
        # Pollingni boshlash
        # chat_join_request va my_chat_member larni o'tkazib yubormaslik uchun allowed_updates
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
                "callback_query",
                "chat_join_request",
                "my_chat_member",
                "chat_member"
            ]
        )
    finally:
        penalty_task.cancel()
        if web_runner:
            await web_runner.cleanup()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
