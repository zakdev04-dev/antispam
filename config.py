import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/anti_spam_bot")
PORT = int(os.getenv("PORT", "8080"))

# Adminlar ro'yxati (vergul bilan ajratilgan IDlar)
ADMINS_RAW = os.getenv("ADMINS", "")
ADMINS = [int(admin_id.strip()) for admin_id in ADMINS_RAW.split(",") if admin_id.strip().isdigit()]

# Default narxlar
VIDEO_PRICE = int(os.getenv("VIDEO_PRICE", "15000"))
DEFAULT_REFERRAL_PRICE = 1000
DEFAULT_TASK_PRICE = 500
PENALTY_FEE = int(os.getenv("PENALTY_FEE", "250"))
