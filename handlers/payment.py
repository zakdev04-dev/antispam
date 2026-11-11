import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import config
from states.user_states import PaymentState
from keyboards.default import cancel_keyboard, main_menu_keyboard
from keyboards.inline import payment_confirm_keyboard

router = Router()
logger = logging.getLogger(__name__)

# --- TO'LOV BOSHLASH ---
@router.callback_query(F.data == "top_up_balance")
async def start_top_up(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(PaymentState.waiting_for_amount)
    await callback.message.answer(
        "💳 <b>Hisobni to'ldirish</b>\n\n"
        "Qancha summaga hisobingizni to'ldirmoqchisiz?\n"
        "Iltimos, summani so'mda (raqamlar bilan) kiriting:\n"
        "<i>(Masalan: 15000 yoki 50000)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(PaymentState.waiting_for_amount, F.text == "❌ Bekor qilish")
async def cancel_payment_amount(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("To'lov bekor qilindi.", reply_markup=main_menu_keyboard())

@router.message(PaymentState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    text = message.text.replace(" ", "").replace(",", "").replace(".", "")
    if not text.isdigit() or int(text) < 1000:
        await message.answer(
            "⚠️ Iltimos, to'g'ri summa kiriting! Minimal to'lov miqdori: 1,000 UZS.\n"
            "Raqamlar bilan kiriting (Masalan: 15000):"
        )
        return

    amount = int(text)
    await state.update_data(amount=amount)

    card_number = await db.get_setting("card_number") or "8600 0000 0000 0000"
    card_holder = await db.get_setting("card_holder") or "ADMIN"
    user_name = message.from_user.first_name or "Foydalanuvchi"

    payment_info = (
        f"Hurmatli <b>{user_name}</b>, siz admin kiritgan karta:\n"
        f"💳 <code>{card_number}</code>\n"
        f"👤 Egasi: <b>{card_holder}</b>\n\n"
        f"Kiritilgan summa: <b>{amount:,} UZS</b>.\n\n"
        f"To'lovni amalga oshiring va <b>to'lov chekini</b> (skrinshot yoki rasm) shu yerga yuboring:"
    )

    await state.set_state(PaymentState.waiting_for_receipt)
    await message.answer(payment_info, reply_markup=cancel_keyboard(), parse_mode="HTML")

@router.message(PaymentState.waiting_for_receipt, F.text == "❌ Bekor qilish")
async def cancel_payment_receipt(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("To'lov bekor qilindi.", reply_markup=main_menu_keyboard())

@router.message(PaymentState.waiting_for_receipt, F.photo)
async def process_photo_receipt(message: Message, state: FSMContext, bot: Bot):
    photo_id = message.photo[-1].file_id
    await save_and_notify_admins(message, state, bot, photo_id, "photo")

@router.message(PaymentState.waiting_for_receipt, F.document)
async def process_doc_receipt(message: Message, state: FSMContext, bot: Bot):
    doc_id = message.document.file_id
    await save_and_notify_admins(message, state, bot, doc_id, "document")

@router.message(PaymentState.waiting_for_receipt)
async def invalid_receipt(message: Message):
    await message.answer(
        "⚠️ Iltimos, to'lov chekini rasm (skrinshot) yoki hujjat ko'rinishida yuboring!"
    )

async def save_and_notify_admins(message: Message, state: FSMContext, bot: Bot, file_id: str, file_type: str):
    data = await state.get_data()
    amount = data.get("amount", 0)
    user_id = message.from_user.id
    name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "yo'q"

    payment_id = await db.create_payment_request(user_id, amount, file_id, file_type)
    await state.clear()

    await message.answer(
        "✅ <b>To'lov cheki qabul qilindi!</b>\n\n"
        "Adminlarimiz chekni tekshirgandan so'ng hisobingizga mablag' qo'shiladi "
        "va sizga xabar beriladi. Iltimos, kuting!",
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML"
    )

    # Adminlarga xabar yuborish
    admin_caption = (
        f"💰 <b>Yangi to'lov so'rovi!</b>\n\n"
        f"🆔 To'lov ID: <code>{payment_id}</code>\n"
        f"👤 Foydalanuvchi: <b>{name}</b> ({username})\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"💵 Summa: <b>{amount:,} UZS</b>\n\n"
        f"Iltimos, chekni tekshirib qaror qabul qiling:"
    )

    for admin_id in config.ADMINS:
        try:
            if file_type == "photo":
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=file_id,
                    caption=admin_caption,
                    reply_markup=payment_confirm_keyboard(payment_id),
                    parse_mode="HTML"
                )
            else:
                await bot.send_document(
                    chat_id=admin_id,
                    document=file_id,
                    caption=admin_caption,
                    reply_markup=payment_confirm_keyboard(payment_id),
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.warning(f"Adminga to'lov xabarini yuborishda xatolik ({admin_id}): {e}")

# --- ADMIN TASDIQLASH / BEKOR QILISH ---
@router.callback_query(F.data.startswith("pay_approve:"))
async def approve_payment(callback: CallbackQuery, bot: Bot):
    payment_id = callback.data.split(":")[1]
    payment = await db.get_payment(payment_id)

    if not payment:
        await callback.answer("To'lov topilmadi!", show_alert=True)
        return

    if payment.get("status") != "pending":
        await callback.answer("Bu to'lovga allaqachon javob berilgan!", show_alert=True)
        return

    user_id = payment["user_id"]
    amount = payment["amount"]

    await db.update_payment_status(payment_id, "approved")
    await db.update_user_balance(user_id, amount)

    user = await db.get_user(user_id)
    new_balance = user.get("balance", 0) if user else amount

    # Foydalanuvchiga xabar
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ <b>To'lovingiz tasdiqlandi!</b>\n\n"
                f"Hisobingizga <b>+{amount:,} UZS</b> qo'shildi.\n"
                f"Joriy balansingiz: <b>{new_balance:,} UZS</b>.\n\n"
                f"<i>Botdan unumli foydalanishingizni tilaymiz!</i>"
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Foydalanuvchiga to'lov tasdiq xabarini yuborib bo'lmadi ({user_id}): {e}")

    await callback.message.edit_caption(
        caption=(
            f"{callback.message.caption}\n\n"
            f"✅ <b>TASDIQLANDI!</b> (+{amount:,} UZS hisobga qo'shildi)\n"
            f"Admin: {callback.from_user.full_name}"
        ),
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer("To'lov muvaffaqiyatli tasdiqlandi!")

@router.callback_query(F.data.startswith("pay_reject:"))
async def reject_payment(callback: CallbackQuery, bot: Bot):
    payment_id = callback.data.split(":")[1]
    payment = await db.get_payment(payment_id)

    if not payment:
        await callback.answer("To'lov topilmadi!", show_alert=True)
        return

    if payment.get("status") != "pending":
        await callback.answer("Bu to'lovga allaqachon javob berilgan!", show_alert=True)
        return

    user_id = payment["user_id"]
    amount = payment["amount"]

    await db.update_payment_status(payment_id, "rejected")

    # Foydalanuvchiga xabar
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"❌ <b>To'lovingiz bekor qilindi!</b>\n\n"
                f"Kiritilgan summa: {amount:,} UZS.\n"
                f"Agar bu xatolik deb hisoblasangiz, adminga murojaat qiling."
            ),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.warning(f"Foydalanuvchiga to'lov rad etish xabarini yuborib bo'lmadi ({user_id}): {e}")

    await callback.message.edit_caption(
        caption=(
            f"{callback.message.caption}\n\n"
            f"❌ <b>BEKOR QILINDI!</b>\n"
            f"Admin: {callback.from_user.full_name}"
        ),
        reply_markup=None,
        parse_mode="HTML"
    )
    await callback.answer("To'lov bekor qilindi!")
