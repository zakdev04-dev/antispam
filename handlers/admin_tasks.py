import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from filters.admin import IsAdmin
from states.admin_states import AddTaskState
from keyboards.admin_kb import task_type_inline_kb, manage_tasks_keyboard, admin_main_keyboard
from keyboards.default import cancel_keyboard

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

logger = logging.getLogger(__name__)

# --- VAZIFA QO'SHISH ---
@router.message(F.text == "📋 Vazifa qo'shish")
async def start_add_task(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📋 <b>Yangi vazifa qo'shish bo'limi</b>\n\n"
        "Vazifa turini tanlang:\n"
        "<i>(Telegram kanal, guruh yoki zayafkali kanal)</i>",
        reply_markup=task_type_inline_kb(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("task_type:"))
async def choose_task_type(callback: CallbackQuery, state: FSMContext):
    task_type = callback.data.split(":")[1]
    await state.update_data(task_type=task_type)
    await state.set_state(AddTaskState.waiting_for_title)

    type_descs = {
        "channel": "Telegram kanal",
        "group": "Telegram guruh",
        "join_request": "Zayafkali kanal"
    }

    await callback.message.delete()
    await callback.message.answer(
        f"Tanlangan vazifa turi: <b>{type_descs.get(task_type)}</b>\n\n"
        f"1️⃣ Vazifa uchun nom (sarlavha) kiriting:\n"
        f"<i>(Masalan: Rasmiy guruhimizga a'zo bo'ling)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AddTaskState.waiting_for_title, F.text == "❌ Bekor qilish")
async def cancel_add_task_title(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Vazifa qo'shish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(AddTaskState.waiting_for_title)
async def process_task_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await state.set_state(AddTaskState.waiting_for_id)
    await message.answer(
        "2️⃣ Kanal yoki guruhning Telegram ID sini yoki @username sini kiriting:\n"
        "<i>(Masalan: -1009876543210 yoki @guruh_nomi)</i>\n\n"
        "⚠️ <b>Eslatma:</b> Bot kanalda/guruhda administrator bo'lishi kerak!",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AddTaskState.waiting_for_id, F.text == "❌ Bekor qilish")
async def cancel_add_task_id(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Vazifa qo'shish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(AddTaskState.waiting_for_id)
async def process_task_id(message: Message, state: FSMContext, bot: Bot):
    raw_id = message.text.strip()
    channel_id = int(raw_id) if (raw_id.startswith("-") and raw_id[1:].isdigit()) or raw_id.isdigit() else raw_id

    try:
        chat = await bot.get_chat(chat_id=channel_id)
        channel_id = chat.id
    except Exception as e:
        logger.warning(f"Vazifa chatini tekshirib bo'lmadi ({channel_id}): {e}")

    await state.update_data(channel_id=channel_id)
    await state.set_state(AddTaskState.waiting_for_url)
    await message.answer(
        "3️⃣ Kanal yoki guruh havolasini (linkini) kiriting:\n"
        "<i>(Masalan: https://t.me/guruh_nomi yoki https://t.me/+AbcDeF...)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AddTaskState.waiting_for_url, F.text == "❌ Bekor qilish")
async def cancel_add_task_url(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Vazifa qo'shish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(AddTaskState.waiting_for_url)
async def process_task_url(message: Message, state: FSMContext):
    url = message.text.strip()
    default_price = await db.get_setting("task_price") or 500
    await state.update_data(url=url)
    await state.set_state(AddTaskState.waiting_for_reward)
    await message.answer(
        f"4️⃣ Ushbu vazifani bajargan foydalanuvchiga beriladigan mukofot summasini kiriting (UZS):\n"
        f"<i>(Standart: {default_price:,} UZS)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(AddTaskState.waiting_for_reward, F.text == "❌ Bekor qilish")
async def cancel_add_task_reward(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Vazifa qo'shish bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(AddTaskState.waiting_for_reward)
async def process_task_reward(message: Message, state: FSMContext):
    text = message.text.replace(" ", "").replace(",", "")
    default_price = await db.get_setting("task_price") or 500
    reward = int(text) if text.isdigit() else default_price

    data = await state.get_data()
    title = data.get("title")
    task_type = data.get("task_type")
    channel_id = data.get("channel_id")
    url = data.get("url")

    await db.add_task(
        title=title,
        task_type=task_type,
        channel_id=channel_id,
        url=url,
        reward=reward
    )

    await state.clear()
    await message.answer(
        f"✅ <b>Yangi vazifa muvaffaqiyatli qo'shildi!</b>\n\n"
        f"📌 Nomi: <b>{title}</b>\n"
        f"🔖 Turi: <code>{task_type}</code>\n"
        f"💰 Mukofot: <b>{reward:,} UZS</b>\n"
        f"🔗 Havola: {url}",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )

# --- VAZIFALARNI BOSHQARISH ---
@router.message(F.text == "🗂 Vazifalarni boshqarish")
async def manage_tasks(message: Message):
    tasks = await db.get_active_tasks()
    if not tasks:
        await message.answer("Hozircha faol vazifalar mavjud emas.")
        return

    text = (
        "🗂 <b>Faol vazifalar ro'yxati:</b>\n\n"
        "O'chirmoqchi bo'lgan vazifangiz ustiga bosing:"
    )
    await message.answer(text, reply_markup=manage_tasks_keyboard(tasks), parse_mode="HTML")

@router.callback_query(F.data.startswith("del_task:"))
async def delete_task_callback(callback: CallbackQuery):
    t_id = callback.data.split(":")[1]
    task = await db.get_task_by_id(t_id)
    title = task.get("title") if task else "Vazifa"

    await db.delete_task(t_id)
    await callback.answer(f"'{title}' o'chirildi!", show_alert=True)

    tasks = await db.get_active_tasks()
    if tasks:
        await callback.message.edit_text(
            "🗂 <b>Faol vazifalar ro'yxati:</b>\n\nO'chirmoqchi bo'lgan vazifangiz ustiga bosing:",
            reply_markup=manage_tasks_keyboard(tasks),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text("Barcha vazifalar o'chirildi.", reply_markup=None)
