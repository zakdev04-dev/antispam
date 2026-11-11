import asyncio
import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

import database as db
from filters.admin import IsAdmin
from states.admin_states import BroadcastState
from keyboards.admin_kb import broadcast_confirm_keyboard, admin_main_keyboard
from keyboards.default import cancel_keyboard, yes_no_keyboard
from keyboards.inline import custom_ad_keyboard

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

logger = logging.getLogger(__name__)

# --- XABAR YUBORISHNI BOSHLASH ---
@router.message(F.text == "✉️ Xabar yuborish")
async def start_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer(
        "✉️ <b>Foydalanuvchilarga xabar yuborish (Rassilka)</b>\n\n"
        "Yubormoqchi bo'lgan xabaringizni (matn, rasm yoki video) yuboring:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(BroadcastState.waiting_for_message, F.text == "❌ Bekor qilish")
async def cancel_broadcast(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Xabar yuborish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(BroadcastState.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    content_type = "text"
    file_id = None
    caption = message.html_text if message.text else message.caption

    if message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id

    await state.update_data(
        content_type=content_type,
        file_id=file_id,
        text=caption
    )

    await state.set_state(BroadcastState.waiting_for_button_choice)
    await message.answer(
        "🔘 Xabarga <b>havola tugmasi (URL button)</b> qo'shilsinmi?",
        reply_markup=yes_no_keyboard(),
        parse_mode="HTML"
    )

@router.message(BroadcastState.waiting_for_button_choice, F.text == "❌ Bekor qilish")
async def cancel_button_choice(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Xabar yuborish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(BroadcastState.waiting_for_button_choice)
async def process_button_choice(message: Message, state: FSMContext):
    choice = message.text.lower()
    if "ha" in choice:
        await state.update_data(has_button=True)
        await state.set_state(BroadcastState.waiting_for_button_text)
        await message.answer(
            "Tugma matnini kiriting:\n<i>(Masalan: Kanalga o'tish)</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
    else:
        await state.update_data(has_button=False, button_text=None, button_url=None)
        await show_broadcast_preview(message, state)

@router.message(BroadcastState.waiting_for_button_text, F.text == "❌ Bekor qilish")
async def cancel_button_text(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Xabar yuborish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(BroadcastState.waiting_for_button_text)
async def process_button_text(message: Message, state: FSMContext):
    btn_text = message.text.strip()
    await state.update_data(button_text=btn_text)
    await state.set_state(BroadcastState.waiting_for_button_url)
    await message.answer(
        "Tugma havolasini (URL) kiriting:\n<i>(Masalan: https://t.me/kanal_nomi)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(BroadcastState.waiting_for_button_url, F.text == "❌ Bekor qilish")
async def cancel_button_url(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Xabar yuborish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(BroadcastState.waiting_for_button_url)
async def process_button_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("t.me")):
        await message.answer("⚠️ Iltimos, haqiqiy havola (URL) kiriting:")
        return

    await state.update_data(button_url=url)
    await show_broadcast_preview(message, state)

async def show_broadcast_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    content_type = data.get("content_type")
    file_id = data.get("file_id")
    text = data.get("text") or ""
    has_button = data.get("has_button", False)

    markup = None
    if has_button:
        markup = custom_ad_keyboard(data.get("button_text"), data.get("button_url"))

    await message.answer("👀 <b>Xabarning ko'rinishi (Preview):</b>", parse_mode="HTML")

    if content_type == "photo":
        await message.answer_photo(photo=file_id, caption=text, reply_markup=markup, parse_mode="HTML")
    elif content_type == "video":
        await message.answer_video(video=file_id, caption=text, reply_markup=markup, parse_mode="HTML")
    else:
        await message.answer(text=text, reply_markup=markup, parse_mode="HTML")

    await state.set_state(BroadcastState.waiting_for_confirm)
    await message.answer(
        "Barcha foydalanuvchilarga yuborilsinmi?",
        reply_markup=broadcast_confirm_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(BroadcastState.waiting_for_confirm, F.data == "broadcast_confirm")
async def execute_broadcast(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await state.clear()

    content_type = data.get("content_type")
    file_id = data.get("file_id")
    text = data.get("text") or ""
    has_button = data.get("has_button", False)

    markup = None
    if has_button:
        markup = custom_ad_keyboard(data.get("button_text"), data.get("button_url"))

    await callback.message.edit_text("🚀 Xabar yuborish boshlandi, iltimos kuting...")

    cursor = await db.get_all_users_cursor()
    success_count = 0
    blocked_count = 0

    async for user in cursor:
        uid = user.get("user_id")
        try:
            if content_type == "photo":
                await bot.send_photo(chat_id=uid, photo=file_id, caption=text, reply_markup=markup, parse_mode="HTML")
            elif content_type == "video":
                await bot.send_video(chat_id=uid, video=file_id, caption=text, reply_markup=markup, parse_mode="HTML")
            else:
                await bot.send_message(chat_id=uid, text=text, reply_markup=markup, parse_mode="HTML")
            success_count += 1
            await asyncio.sleep(0.04)  # Telegram limits
        except TelegramForbiddenError:
            blocked_count += 1
            await db.update_user_status(uid, False)
        except Exception:
            blocked_count += 1

    report = (
        f"✅ <b>Xabar yuborish yakunlandi!</b>\n\n"
        f"📨 Muvaffaqiyatli yetkazildi: <b>{success_count}</b> ta\n"
        f"🚫 Bloklagan yoki yetib bormagan: <b>{blocked_count}</b> ta"
    )

    await callback.message.answer(report, reply_markup=admin_main_keyboard(), parse_mode="HTML")

@router.callback_query(BroadcastState.waiting_for_confirm, F.data == "broadcast_cancel")
async def cancel_broadcast_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Xabar yuborish bekor qilindi.")
    await callback.message.answer("Asosiy panel:", reply_markup=admin_main_keyboard())
