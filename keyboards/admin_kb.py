from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def admin_main_keyboard() -> ReplyKeyboardMarkup:
    """
    Admin paneli asosiy klaviaturasi:
    kanal ulash, kanallarni boshqarish, statistika, video joylash,
    xabar yuborish, reklama joylash, vazifa qo'shish, referal narxi, vazifa narxi
    va qo'shimcha boshqaruvlar.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Kanal ulash"), KeyboardButton(text="⚙️ Kanallarni boshqarish")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="✉️ Xabar yuborish")],
            [KeyboardButton(text="📹 Video joylash"), KeyboardButton(text="📢 Reklama joylash")],
            [KeyboardButton(text="📋 Vazifa qo'shish"), KeyboardButton(text="🗂 Vazifalarni boshqarish")],
            [KeyboardButton(text="💰 Referal narxi"), KeyboardButton(text="💵 Vazifa narxi")],
            [KeyboardButton(text="💳 Karta ma'lumotlari")],
            [KeyboardButton(text="ℹ️ Bot haqida matni"), KeyboardButton(text="🆘 Yordam matni")],
            [KeyboardButton(text="🔙 Foydalanuvchi rejimi")]
        ],
        resize_keyboard=True
    )

def channel_type_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Ochiq kanal (@username)", callback_data="ch_type:public")],
            [InlineKeyboardButton(text="🔒 Shaxsiy (Private) kanal", callback_data="ch_type:private")],
            [InlineKeyboardButton(text="📥 Zayafkali kanal (Join request)", callback_data="ch_type:join_request")],
            [InlineKeyboardButton(text="🌐 Tashqi link (Web havola)", callback_data="ch_type:external")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")]
        ]
    )

def task_type_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Telegram kanal", callback_data="task_type:channel")],
            [InlineKeyboardButton(text="👥 Telegram guruh", callback_data="task_type:group")],
            [InlineKeyboardButton(text="📥 Zayafkali kanal", callback_data="task_type:join_request")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")]
        ]
    )

def manage_channels_keyboard(channels: list) -> InlineKeyboardMarkup:
    keyboard = []
    for ch in channels:
        ch_id = str(ch["_id"])
        title = ch.get("title", "Kanal")
        ch_type = ch.get("type", "")
        keyboard.append([
            InlineKeyboardButton(text=f"🗑 {title} ({ch_type})", callback_data=f"del_channel:{ch_id}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Yopish", callback_data="admin_close")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def manage_tasks_keyboard(tasks: list) -> InlineKeyboardMarkup:
    keyboard = []
    for t in tasks:
        t_id = str(t["_id"])
        title = t.get("title", "Vazifa")
        reward = t.get("reward", 0)
        keyboard.append([
            InlineKeyboardButton(text=f"🗑 {title} ({reward:,} UZS)", callback_data=f"del_task:{t_id}")
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Yopish", callback_data="admin_close")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def broadcast_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Yuborishni boshlash", callback_data="broadcast_confirm"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="broadcast_cancel")
            ]
        ]
    )
