from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Kontaktni ulashish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Foydalanuvchi interfeysi:
        video qo'llanma
        kabinet     taklif havola
        reklama     bot haqida
                    yordam
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📹 Video qo'llanma")],
            [KeyboardButton(text="👤 Kabinet"), KeyboardButton(text="🔗 Taklif havola")],
            [KeyboardButton(text="📢 Reklama"), KeyboardButton(text="ℹ️ Bot haqida")],
            [KeyboardButton(text="🆘 Yordam")]
        ],
        resize_keyboard=True
    )

def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

def yes_no_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q")]
        ],
        resize_keyboard=True
    )
