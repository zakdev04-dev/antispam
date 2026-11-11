import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from filters.admin import IsAdmin
from states.admin_states import AddChannelState
from keyboards.admin_kb import channel_type_inline_kb, manage_channels_keyboard, admin_main_keyboard
from keyboards.default import cancel_keyboard

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

logger = logging.getLogger(__name__)

# --- KANAL ULASH ---
@router.message(F.text == "📢 Kanal ulash")
async def start_add_channel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📢 <b>Kanal ulash bo'limi</b>\n\n"
        "Qaysi turdagi kanal yoki havolani ulamoqchisiz?\n"
        "<i>Tugma nomi avtomatik tarzda <b>&lt; Obuna bo'lish &gt;</b> deb o'rnatiladi.</i>",
        reply_markup=channel_type_inline_kb(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("ch_type:"))
async def choose_channel_type(callback: CallbackQuery, state: FSMContext):
    ch_type = callback.data.split(":")[1]
    await state.update_data(ch_type=ch_type)
    await state.set_state(AddChannelState.waiting_for_title)

    type_descs = {
        "public": "Ochiq kanal (@username)",
        "private": "Shaxsiy (Private) kanal",
        "join_request": "Zayafkali kanal (Kirish so'rovi)",
        "external": "Tashqi havola (Web sayt yoki boshqa havola)"
    }

    await callback.message.delete()
    await callback.message.answer(
        f"Tanlangan tur: <b>{type_descs.get(ch_type)}</b>\n\n"
        f"1️⃣ Ushbu kanal/havola uchun nom (sarlavha) kiriting:\n"
        f"<i>(Masalan: Asosiy Yangiliklar kanali)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AddChannelState.waiting_for_title, F.text == "❌ Bekor qilish")
async def cancel_add_channel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Kanal qo'shish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(AddChannelState.waiting_for_title)
async def process_channel_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    data = await state.get_data()
    ch_type = data.get("ch_type")

    if ch_type == "external":
        # Tashqi link uchun kanal ID shart emas
        await state.update_data(channel_id=None)
        await state.set_state(AddChannelState.waiting_for_url)
        await message.answer(
            "2️⃣ Endi to'liq veb-havolani (URL) kiriting:\n"
            "<i>(Masalan: https://example.com yoki https://instagram.com/...)</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
    else:
        await state.set_state(AddChannelState.waiting_for_id)
        await message.answer(
            "2️⃣ Kanalning Telegram ID si yoki @username sini kiriting:\n"
            "<i>(Masalan: -1001234567890 yoki @kanal_username)</i>\n\n"
            "⚠️ <b>Muhim:</b> Bot ushbu kanalda administrator bo'lishi shart!",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )

@router.message(AddChannelState.waiting_for_id, F.text == "❌ Bekor qilish")
async def cancel_add_channel_id(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Kanal qo'shish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(AddChannelState.waiting_for_id)
async def process_channel_id(message: Message, state: FSMContext, bot: Bot):
    raw_id = message.text.strip()
    channel_id = int(raw_id) if (raw_id.startswith("-") and raw_id[1:].isdigit()) or raw_id.isdigit() else raw_id

    # Botning ushbu kanalda admin ekanligini tekshirishga urinish
    try:
        chat = await bot.get_chat(chat_id=channel_id)
        channel_id = chat.id
    except Exception as e:
        logger.warning(f"Kanalni tekshirib bo'lmadi ({channel_id}): {e}")
        # Shaxsiy yoki zayafkali kanallarda ham davom etishga ruxsat beramiz

    await state.update_data(channel_id=channel_id)
    await state.set_state(AddChannelState.waiting_for_url)
    await message.answer(
        "3️⃣ Endi foydalanuvchilar o'tishi uchun kanal havolasini (linkini) kiriting:\n"
        "<i>(Masalan: https://t.me/joinchat/... yoki https://t.me/+AbCdEf...)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AddChannelState.waiting_for_url, F.text == "❌ Bekor qilish")
async def cancel_add_channel_url(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Kanal qo'shish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(AddChannelState.waiting_for_url)
async def process_channel_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("t.me")):
        await message.answer("⚠️ Iltimos, haqiqiy URL manzil kiriting (https://...):")
        return

    data = await state.get_data()
    title = data.get("title")
    ch_type = data.get("ch_type")
    channel_id = data.get("channel_id")
    btn_name = "< Obuna bo'lish >"

    await db.add_channel(
        title=title,
        ch_type=ch_type,
        channel_id=channel_id,
        url=url,
        button_name=btn_name
    )

    await state.clear()
    await message.answer(
        f"✅ <b>Kanal muvaffaqiyatli ulandi!</b>\n\n"
        f"📌 Nomi: <b>{title}</b>\n"
        f"🔖 Turi: <code>{ch_type}</code>\n"
        f"🔗 Havola: {url}\n"
        f"🔘 Tugma nomi: <b>{btn_name}</b>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )

# --- KANALLARNI BOSHQARISH (O'CHIRISH) ---
@router.message(F.text == "⚙️ Kanallarni boshqarish")
async def manage_channels(message: Message):
    channels = await db.get_channels()
    if not channels:
        await message.answer("Hozircha ulangan majburiy kanallar yo'q.")
        return

    text = (
        "⚙️ <b>Ulangan kanallar ro'yxati:</b>\n\n"
        "O'chirmoqchi bo'lgan kanalingiz ustiga bosing:"
    )
    await message.answer(text, reply_markup=manage_channels_keyboard(channels), parse_mode="HTML")

@router.callback_query(F.data.startswith("del_channel:"))
async def delete_channel_callback(callback: CallbackQuery):
    ch_id = callback.data.split(":")[1]
    channel = await db.get_channel_by_id(ch_id)
    title = channel.get("title") if channel else "Kanal"

    await db.delete_channel(ch_id)
    await callback.answer(f"'{title}' o'chirildi!", show_alert=True)

    channels = await db.get_channels()
    if channels:
        await callback.message.edit_text(
            "⚙️ <b>Ulangan kanallar ro'yxati:</b>\n\nO'chirmoqchi bo'lgan kanalingiz ustiga bosing:",
            reply_markup=manage_channels_keyboard(channels),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text("Barcha kanallar o'chirildi.", reply_markup=None)
