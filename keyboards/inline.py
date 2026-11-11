import urllib.parse
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def mandatory_channels_keyboard(unsubscribed_channels: list) -> InlineKeyboardMarkup:
    """
    Foydalanuvchi faqat obuna bo'lmagan kanallar ko'rsatiladi.
    Tugma nomi qat'iy talabga ko'ra: < Obuna bo'lish >
    """
    keyboard = []
    for ch in unsubscribed_channels:
        # Tashqi havola bo'lsa callback yoki to'g'ridan to'g'ri url
        url = ch.get("url", "https://t.me")
        btn_name = ch.get("button_name") or "< Obuna bo'lish >"
        keyboard.append([
            InlineKeyboardButton(text=btn_name, url=url)
        ])

    # Tekshirish tugmasi
    keyboard.append([
        InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_subscription")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def cabinet_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="top_up_balance"),
                InlineKeyboardButton(text="📋 Vazifalar", callback_data="view_tasks")
            ]
        ]
    )

def fill_balance_quick_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💳 Hisobni to'ldirish", callback_data="top_up_balance")]
        ]
    )

def payment_confirm_keyboard(payment_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"pay_approve:{payment_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"pay_reject:{payment_id}")
            ]
        ]
    )

def tasks_list_keyboard(tasks: list) -> InlineKeyboardMarkup:
    keyboard = []
    for idx, t in enumerate(tasks, 1):
        keyboard.append([
            InlineKeyboardButton(
                text=f"{idx}. {t.get('title', 'Vazifa')} (+{t.get('reward', 0):,} UZS)",
                callback_data=f"task_view:{str(t['_id'])}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def task_action_keyboard(task_url: str, task_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔗 O'tish va obuna bo'lish", url=task_url)],
            [InlineKeyboardButton(text="✅ Vazifani tekshirish", callback_data=f"task_check:{task_id}")],
            [InlineKeyboardButton(text="🔙 Vazifalar ro'yxati", callback_data="view_tasks")]
        ]
    )

def share_referral_keyboard(bot_username: str, user_id: int) -> InlineKeyboardMarkup:
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    share_text = f"🔥 Zo'r bot topdim! Video qo'llanmalar, vazifalar va daromad olish imkoniyati!\nHoziroq kiring: {ref_link}"
    encoded_text = urllib.parse.quote(share_text)
    share_url = f"https://t.me/share/url?url={ref_link}&text={encoded_text}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Do'stlarga ulashish", url=share_url)]
        ]
    )

def custom_ad_keyboard(button_text: str, button_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button_text, url=button_url)]
        ]
    )
