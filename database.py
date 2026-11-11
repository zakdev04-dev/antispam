from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import config

client = None
db = None

# Toshkent vaqt zonasi (UTC+5)
TASHKENT_TZ = timezone(timedelta(hours=5))

def get_current_time():
    return datetime.now(TASHKENT_TZ)

async def init_db():
    global client, db
    client = AsyncIOMotorClient(config.MONGO_URI)
    # Database nomini ajratib olish yoki standart database
    db_name = "anti_spam_bot"
    try:
        db = client.get_default_database()
    except Exception:
        db = client[db_name]

    # Indekslar yaratish
    await db.users.create_index("user_id", unique=True)
    await db.channels.create_index("channel_id")
    await db.join_requests.create_index([("user_id", 1), ("channel_id", 1)])
    await db.user_tasks.create_index([("user_id", 1), ("task_id", 1)])
    await db.user_tasks.create_index("completed_at")
    await db.settings.create_index("key", unique=True)

    # Standart sozlamalarni tekshirish va yaratish
    await ensure_default_settings()

async def ensure_default_settings():
    defaults = {
        "referral_price": config.DEFAULT_REFERRAL_PRICE,
        "task_price": config.DEFAULT_TASK_PRICE,
        "card_number": "8600 0000 0000 0000",
        "card_holder": "ADMIN CARD",
        "video_guide": {
            "file_id": None,
            "caption": "📹 Maxsus video qo'llanma!\nUshbu qo'llanmada barcha zarur ko'rsatmalar berilgan."
        },
        "ad_post": {
            "text": "📢 Bu yerda sizning reklamangiz bo'lishi mumkin!\nReklama joylashtirish uchun adminga murojaat qiling.",
            "file_id": None,
            "file_type": None,
            "has_button": False,
            "button_text": None,
            "button_url": None
        },
        "about_text": (
            "🤖 <b>Bot haqida</b>\n\n"
            "Bu bot orqali siz qulay va oson tarzda video qo'llanmalarni olishingiz, "
            "vazifalarni bajarib pul ishlashingiz, do'stlaringizni taklif qilib "
            "balansingizni oshirishingiz mumkin!\n\n"
            "🌟 <b>Afzalliklari:</b>\n"
            "• Tezkor va xavfsiz to'lovlar\n"
            "• Qiziqarli va daromadli vazifalar\n"
            "• Foydali video qo'llanmalar\n"
            "• 24/7 faol tizim"
        ),
        "help_text": (
            "🆘 <b>Yordam va Murojaat</b>\n\n"
            "Savol, taklif yoki to'lov bo'yicha muammo bormi?\n"
            "Admin bilan bog'lanish: @admin\n"
            "Biz sizga doim yordam berishga tayyormiz!"
        )
    }

    for key, value in defaults.items():
        existing = await db.settings.find_one({"key": key})
        if not existing:
            await db.settings.insert_one({"key": key, "value": value})

# --- USER OPERATIONS ---
async def get_user(user_id: int):
    return await db.users.find_one({"user_id": user_id})

async def add_or_update_user(user_id: int, first_name: str, last_name: str = "", username: str = "", referrer_id: int = None):
    user = await get_user(user_id)
    if not user:
        new_user = {
            "user_id": user_id,
            "first_name": first_name or "",
            "last_name": last_name or "",
            "username": username or "",
            "phone": None,
            "balance": 0,
            "referrer_id": referrer_id,
            "referral_rewarded": False,
            "is_active": True,
            "has_video_access": False,
            "created_at": get_current_time(),
            "subscribed_external_links": []
        }
        await db.users.insert_one(new_user)
        return new_user
    else:
        update_data = {
            "first_name": first_name or "",
            "last_name": last_name or "",
            "username": username or "",
            "is_active": True
        }
        await db.users.update_one({"user_id": user_id}, {"$set": update_data})
        return await get_user(user_id)

async def set_user_phone(user_id: int, phone: str):
    await db.users.update_one({"user_id": user_id}, {"$set": {"phone": phone}})

async def update_user_status(user_id: int, is_active: bool):
    await db.users.update_one({"user_id": user_id}, {"$set": {"is_active": is_active}})

async def update_user_balance(user_id: int, amount: float):
    await db.users.update_one({"user_id": user_id}, {"$inc": {"balance": amount}})

async def set_video_access(user_id: int, access: bool = True):
    await db.users.update_one({"user_id": user_id}, {"$set": {"has_video_access": access}})

async def add_external_link_click(user_id: int, channel_str_id: str):
    await db.users.update_one(
        {"user_id": user_id},
        {"$addToSet": {"subscribed_external_links": channel_str_id}}
    )

# --- STATS OPERATIONS ---
async def get_statistics():
    total_users = await db.users.count_documents({})
    active_users = await db.users.count_documents({"is_active": True})
    blocked_users = await db.users.count_documents({"is_active": False})

    # Bugungi yangi foydalanuvchilar (Toshkent vaqti bilan kun boshi)
    now = get_current_time()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=TASHKENT_TZ)
    today_users = await db.users.count_documents({"created_at": {"$gte": today_start}})

    total_channels = await db.channels.count_documents({})
    total_tasks = await db.tasks.count_documents({"is_active": True})

    return {
        "total_users": total_users,
        "active_users": active_users,
        "blocked_users": blocked_users,
        "today_users": today_users,
        "total_channels": total_channels,
        "total_tasks": total_tasks
    }

# --- CHANNELS (MANDATORY SUBSCRIPTION) ---
async def add_channel(title: str, ch_type: str, channel_id, url: str, button_name: str = "< Obuna bo'lish >"):
    new_ch = {
        "title": title,
        "type": ch_type,  # 'public', 'private', 'join_request', 'external'
        "channel_id": channel_id,
        "url": url,
        "button_name": button_name,
        "created_at": get_current_time()
    }
    result = await db.channels.insert_one(new_ch)
    return str(result.inserted_id)

async def get_channels():
    cursor = db.channels.find({})
    return await cursor.to_list(length=100)

async def get_channel_by_id(ch_id: str):
    try:
        return await db.channels.find_one({"_id": ObjectId(ch_id)})
    except Exception:
        return None

async def delete_channel(ch_id: str):
    try:
        await db.channels.delete_one({"_id": ObjectId(ch_id)})
        return True
    except Exception:
        return False

# --- JOIN REQUESTS (ZAYAVKALAR) ---
async def save_join_request(user_id: int, channel_id: int):
    await db.join_requests.update_one(
        {"user_id": user_id, "channel_id": channel_id},
        {"$set": {"status": "pending", "updated_at": get_current_time()}},
        upsert=True
    )

async def check_join_request_exists(user_id: int, channel_id: int):
    doc = await db.join_requests.find_one({"user_id": user_id, "channel_id": channel_id})
    return doc is not None

# --- TASKS (VAZIFALAR) ---
async def add_task(title: str, task_type: str, channel_id, url: str, reward: int):
    new_task = {
        "title": title,
        "task_type": task_type,  # 'channel', 'group', 'join_request'
        "channel_id": channel_id,
        "url": url,
        "reward": reward,
        "is_active": True,
        "created_at": get_current_time()
    }
    result = await db.tasks.insert_one(new_task)
    return str(result.inserted_id)

async def get_active_tasks():
    cursor = db.tasks.find({"is_active": True})
    return await cursor.to_list(length=100)

async def get_task_by_id(task_id: str):
    try:
        return await db.tasks.find_one({"_id": ObjectId(task_id)})
    except Exception:
        return None

async def delete_task(task_id: str):
    try:
        await db.tasks.delete_one({"_id": ObjectId(task_id)})
        return True
    except Exception:
        return False

# --- USER TASK COMPLETION & PENALTY ---
async def is_task_completed_by_user(user_id: int, task_id: str):
    doc = await db.user_tasks.find_one({"user_id": user_id, "task_id": task_id})
    return doc is not None

async def complete_task_for_user(user_id: int, task_id: str, channel_id, reward: int):
    record = {
        "user_id": user_id,
        "task_id": task_id,
        "channel_id": channel_id,
        "reward": reward,
        "completed_at": get_current_time(),
        "penalized": False
    }
    await db.user_tasks.insert_one(record)
    await update_user_balance(user_id, reward)

async def get_recent_completed_tasks_for_penalty():
    # Oxirgi 30 kun ichida bajarilgan va hali jarima qilinmagan vazifalar
    cutoff = get_current_time() - timedelta(days=30)
    cursor = db.user_tasks.find({
        "completed_at": {"$gte": cutoff},
        "penalized": False
    })
    return await cursor.to_list(length=1000)

async def mark_task_penalized(record_id):
    await db.user_tasks.update_one({"_id": record_id}, {"$set": {"penalized": True}})

# --- PAYMENTS ---
async def create_payment_request(user_id: int, amount: int, file_id: str, file_type: str = "photo"):
    doc = {
        "user_id": user_id,
        "amount": amount,
        "file_id": file_id,
        "file_type": file_type,
        "status": "pending",
        "created_at": get_current_time()
    }
    res = await db.payments.insert_one(doc)
    return str(res.inserted_id)

async def get_payment(payment_id: str):
    try:
        return await db.payments.find_one({"_id": ObjectId(payment_id)})
    except Exception:
        return None

async def update_payment_status(payment_id: str, status: str):
    try:
        await db.payments.update_one({"_id": ObjectId(payment_id)}, {"$set": {"status": status}})
        return True
    except Exception:
        return False

# --- SETTINGS GET / SET ---
async def get_setting(key: str):
    doc = await db.settings.find_one({"key": key})
    if doc:
        return doc.get("value")
    return None

async def set_setting(key: str, value):
    await db.settings.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)

async def get_all_users_cursor():
    return db.users.find({})
