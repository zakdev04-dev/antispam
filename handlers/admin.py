import logging
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
from filters.admin import IsAdmin
from keyboards.admin_kb import admin_main_keyboard
from keyboards.default import main_menu_keyboard

router = Router()
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

logger = logging.getLogger(__name__)

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "👑 <b>Admin Boshqaruv Paneliga Xush Kelibsiz!</b>\n\n"
        "Quyidagi bo'limlardan birini tanlang:"
    )
    await message.answer(text, reply_markup=admin_main_keyboard(), parse_mode="HTML")

@router.message(F.text == "🔙 Foydalanuvchi rejimi")
async def back_to_user_mode(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Siz foydalanuvchi menyusiga o'tdingiz.", reply_markup=main_menu_keyboard())

# --- STATISTIKA ---
@router.message(F.text == "📊 Statistika")
async def show_statistics(message: Message):
    stats = await db.get_statistics()
    now_time = db.get_current_time().strftime("%Y-%m-%d %H:%M")

    text = (
        f"📊 <b>Bot Statistikasi:</b>\n"
        f"<i>(Holat: {now_time})</i>\n\n"
        f"👥 <b>Jami foydalanuvchilar:</b> {stats['total_users']:,} ta\n"
        f"✅ <b>Faol (Active) foydalanuvchilar:</b> {stats['active_users']:,} ta\n"
        f"🚫 <b>Bloklagan foydalanuvchilar:</b> {stats['blocked_users']:,} ta\n"
        f"📅 <b>Bugun qo'shilganlar:</b> {stats['today_users']:,} ta\n\n"
        f"📢 <b>Ulangan majburiy kanallar:</b> {stats['total_channels']:,} ta\n"
        f"📋 <b>Faol vazifalar soni:</b> {stats['total_tasks']:,} ta"
    )

    await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "admin_cancel")
async def callback_admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.callback_query(F.data == "admin_close")
async def callback_admin_close(callback: CallbackQuery):
    await callback.message.delete()
