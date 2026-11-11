import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from keyboards.default import contact_keyboard, main_menu_keyboard
from keyboards.inline import mandatory_channels_keyboard
from services.checker import get_unsubscribed_channels

router = Router()
logger = logging.getLogger(__name__)

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, bot: Bot, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "Foydalanuvchi"
    last_name = message.from_user.last_name or ""
    username = message.from_user.username or ""

    # Referer tekshirish (masalan: /start ref_123456)
    referrer_id = None
    if command.args and command.args.startswith("ref_"):
        ref_raw = command.args.replace("ref_", "")
        if ref_raw.isdigit() and int(ref_raw) != user_id:
            referrer_id = int(ref_raw)

    user = await db.add_or_update_user(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        username=username,
        referrer_id=referrer_id
    )

    # Agar telefon raqami bo'lmasa, kontakt so'rash
    if not user.get("phone"):
        welcome_text = (
            f"Assalomu alaykum, <b>{first_name}</b>!\n\n"
            f"Botimizga xush kelibsiz! Bot imkoniyatlaridan to'liq foydalanish uchun "
            f"iltimos, pastdagi tugma orqali telefon raqamingizni ulashing."
        )
        await message.answer(welcome_text, reply_markup=contact_keyboard(), parse_mode="HTML")
        return

    # Telefon raqami bor bo'lsa, majburiy obunani tekshirish
    await show_channels_or_main_menu(message, bot, user_id)

@router.message(F.contact)
async def handle_contact(message: Message, bot: Bot):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    await db.set_user_phone(user_id, phone)
    await message.answer("✅ Telefon raqamingiz muvaffaqiyatli qabul qilindi!", reply_markup=None)

    # Majburiy obunani tekshirish
    await show_channels_or_main_menu(message, bot, user_id)

async def show_channels_or_main_menu(event: Message | CallbackQuery, bot: Bot, user_id: int):
    unsubscribed = await get_unsubscribed_channels(bot, user_id)

    if unsubscribed:
        text = (
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            "<i>(Obuna bo'lgan kanallaringiz ro'yxatdan avtomatik olib tashlanadi)</i>"
        )
        kb = mandatory_channels_keyboard(unsubscribed)
        if isinstance(event, Message):
            await event.answer(text, reply_markup=kb, parse_mode="HTML")
        else:
            try:
                await event.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
            except Exception:
                await event.message.answer(text, reply_markup=kb, parse_mode="HTML")
    else:
        # Barchasiga obuna bo'lgan
        await reward_referrer_if_needed(bot, user_id)
        text = (
            "🎉 <b>Xush kelibsiz!</b>\n\n"
            "Siz barcha majburiy kanallarga a'zo bo'ldingiz.\n"
            "Quyidagi menyu orqali botdan foydalanishingiz mumkin:"
        )
        if isinstance(event, Message):
            await event.answer(text, reply_markup=main_menu_keyboard(), parse_mode="HTML")
        else:
            try:
                await event.message.delete()
            except Exception:
                pass
            await bot.send_message(user_id, text, reply_markup=main_menu_keyboard(), parse_mode="HTML")

async def reward_referrer_if_needed(bot: Bot, user_id: int):
    user = await db.get_user(user_id)
    if user and user.get("referrer_id") and not user.get("referral_rewarded"):
        referrer_id = user["referrer_id"]
        ref_price = await db.get_setting("referral_price") or 1000

        await db.update_user_balance(referrer_id, ref_price)
        await db.db.users.update_one({"user_id": user_id}, {"$set": {"referral_rewarded": True}})

        try:
            await bot.send_message(
                referrer_id,
                f"🎉 <b>Yangi do'st taklif qilindi!</b>\n\n"
                f"Sizning taklif havolangiz orqali ro'yxatdan o'tgan yangi foydalanuvchi "
                f"barcha shartlarni bajardi. Balansingizga <b>+{ref_price:,} UZS</b> qo'shildi!",
                parse_mode="HTML"
            )
        except Exception:
            pass

@router.callback_query(F.data == "check_subscription")
async def callback_check_subscription(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    unsubscribed = await get_unsubscribed_channels(bot, user_id)

    if unsubscribed:
        await callback.answer("❌ Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
        text = (
            "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            "<i>(Obuna bo'lgan kanallaringiz ro'yxatdan avtomatik olib tashlanadi)</i>"
        )
        kb = mandatory_channels_keyboard(unsubscribed)
        try:
            await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
        except Exception:
            pass
    else:
        await callback.answer("✅ Tabriklaymiz, barcha kanallarga a'zo bo'ldingiz!", show_alert=False)
        await show_channels_or_main_menu(callback, bot, user_id)
