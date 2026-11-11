import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from datetime import datetime

import database as db
import config
from keyboards.inline import cabinet_keyboard, fill_balance_quick_keyboard, share_referral_keyboard, custom_ad_keyboard

router = Router()
logger = logging.getLogger(__name__)

# --- VIDEO QO'LLANMA ---
@router.message(F.text == "📹 Video qo'llanma")
async def handle_video_guide(message: Message, bot: Bot):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    balance = user.get("balance", 0) if user else 0
    price = config.VIDEO_PRICE

    # Video qo'llanma sozlamasini olish
    guide = await db.get_setting("video_guide")
    if not guide or not guide.get("file_id"):
        await message.answer(
            "📹 <b>Video qo'llanma tez orada yuklanadi!</b>\n\nAdmin hozirda yangi material tayyorlamoqda.",
            parse_mode="HTML"
        )
        return

    # Balansni tekshirish (15 000 UZS)
    if balance < price:
        await message.answer(
            f"❌ <b>Hisobingizda mablag' yetarli emas!</b>\n\n"
            f"📹 Video qo'llanma narxi: <b>{price:,} UZS</b>\n"
            f"💳 Sizning balansingiz: <b>{balance:,} UZS</b>\n\n"
            f"Qo'llanmani olish uchun hisobingizni to'ldiring:",
            reply_markup=fill_balance_quick_keyboard(),
            parse_mode="HTML"
        )
        return

    # Balansidan yechib olish
    await db.update_user_balance(user_id, -price)
    await db.set_video_access(user_id, True)

    file_id = guide.get("file_id")
    caption = guide.get("caption") or "📹 Mana siz kutgan video qo'llanma!"

    await message.answer(
        f"✅ Hisobingizdan <b>{price:,} UZS</b> yechildi!\nSizga video qo'llanma yuborilmoqda...",
        parse_mode="HTML"
    )

    try:
        await bot.send_video(
            chat_id=user_id,
            video=file_id,
            caption=f"{caption}\n\n<i>Qo'llanmani yaxshilab o'rganib chiqing!</i>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Videoni yuborishda xatolik: {e}")
        await message.answer("⚠️ Video yuborishda xatolik yuz berdi. Iltimos adminga murojaat qiling.")

# --- KABINET ---
@router.message(F.text == "👤 Kabinet")
async def handle_cabinet(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await message.answer("Iltimos, qayta /start buyrug'ini yuboring.")
        return

    name = user.get("first_name", "") + (" " + user.get("last_name", "") if user.get("last_name") else "")
    username = f"@{user.get('username')}" if user.get("username") else "Mavjud emas"
    phone = user.get("phone", "Kiritilmagan")
    balance = user.get("balance", 0)

    created_at = user.get("created_at")
    if isinstance(created_at, datetime):
        reg_date = created_at.strftime("%Y-%m-%d %H:%M")
    else:
        reg_date = "Noma'lum"

    text = (
        f"👤 <b>Sizning shaxsiy kabinetingiz:</b>\n\n"
        f"🏷 <b>Ism:</b> {name}\n"
        f"🌐 <b>Username:</b> {username}\n"
        f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
        f"📱 <b>Telefon raqam:</b> {phone}\n"
        f"💰 <b>Hisobingiz:</b> <b>{balance:,} UZS</b>\n"
        f"📅 <b>Qo'shilgan sana:</b> {reg_date}\n\n"
        f"<i>Hisobingizni to'ldirishingiz yoki vazifalarni bajarib pul ishlashingiz mumkin!</i>"
    )

    await message.answer(text, reply_markup=cabinet_keyboard(), parse_mode="HTML")

# --- TAKLIF HAVOLA ---
@router.message(F.text == "🔗 Taklif havola")
async def handle_referral(message: Message, bot: Bot):
    user_id = message.from_user.id
    bot_info = await bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user_id}"
    ref_price = await db.get_setting("referral_price") or 1000

    creative_post = (
        f"🚀 <b>Do'stlaringizni taklif qiling va pul ishlang!</b>\n\n"
        f"Har bir taklif qilgan faol do'stingiz uchun sizga <b>{ref_price:,} UZS</b> beriladi! 💸\n\n"
        f"Sizning shaxsiy taklif havolangiz:\n"
        f"👉 <code>{ref_link}</code>\n\n"
        f"🎯 <b>Qanday ishlaydi?</b>\n"
        f"1. Ushbu havolani do'stlaringizga, guruhlarga yoki kanallarga tarqating.\n"
        f"2. Do'stingiz botga kirib, ro'yxatdan o'tadi.\n"
        f"3. U bot shartlarini bajargan zahoti balansingizga pul tushadi!\n\n"
        f"<i>Hoziroq 'Ulashish' tugmasini bosing va do'stlaringizni taklif qilishni boshlang! 👇</i>"
    )

    await message.answer(
        creative_post,
        reply_markup=share_referral_keyboard(bot_info.username, user_id),
        parse_mode="HTML"
    )

# --- REKLAMA BO'LIMI ---
@router.message(F.text == "📢 Reklama")
async def handle_ad_section(message: Message, bot: Bot):
    ad = await db.get_setting("ad_post")
    if not ad:
        await message.answer("📢 Hozircha faol reklama mavjud emas.")
        return

    text = ad.get("text") or "📢 Bu yerda sizning reklamangiz bo'lishi mumkin!"
    file_id = ad.get("file_id")
    file_type = ad.get("file_type")
    has_button = ad.get("has_button", False)

    reply_markup = None
    if has_button and ad.get("button_text") and ad.get("button_url"):
        reply_markup = custom_ad_keyboard(ad["button_text"], ad["button_url"])

    if file_id and file_type == "photo":
        await bot.send_photo(chat_id=message.chat.id, photo=file_id, caption=text, reply_markup=reply_markup, parse_mode="HTML")
    elif file_id and file_type == "video":
        await bot.send_video(chat_id=message.chat.id, video=file_id, caption=text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=reply_markup, parse_mode="HTML")

# --- BOT HAQIDA ---
@router.message(F.text == "ℹ️ Bot haqida")
async def handle_about(message: Message):
    about_text = await db.get_setting("about_text")
    if not about_text:
        about_text = "ℹ️ Bot haqida ma'lumot tez orada yangilanadi."
    await message.answer(about_text, parse_mode="HTML")

# --- YORDAM ---
@router.message(F.text == "🆘 Yordam")
async def handle_help(message: Message):
    help_text = await db.get_setting("help_text")
    if not help_text:
        help_text = "🆘 Yordam xizmati: @admin bilan bog'laning."
    await message.answer(help_text, parse_mode="HTML")
