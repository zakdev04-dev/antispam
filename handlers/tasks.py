import logging
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

import database as db
from keyboards.inline import tasks_list_keyboard, task_action_keyboard
from services.checker import is_subscribed_to_chat

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "view_tasks")
async def show_tasks_list(callback: CallbackQuery):
    tasks = await db.get_active_tasks()
    if not tasks:
        await callback.answer("Hozircha hech qanday faol vazifa mavjud emas.", show_alert=True)
        return

    text = (
        "📋 <b>Mavjud vazifalar ro'yxati:</b>\n\n"
        "Vazifalarni bajarib, hisobingizga pul ishlang!\n"
        "<i>Har bir vazifani tanlab, shartlarini bajaring.</i>\n\n"
        "⚠️ <b>Eslatma:</b> 30 kun ichida kanaldan yoki guruhdan chiqib ketsangiz, "
        "balansingizdan <b>vazifa narxi + 250 UZS</b> jarima yechiladi!"
    )

    await callback.message.edit_text(text, reply_markup=tasks_list_keyboard(tasks), parse_mode="HTML")

@router.callback_query(F.data.startswith("task_view:"))
async def view_single_task(callback: CallbackQuery):
    task_id = callback.data.split(":")[1]
    task = await db.get_task_by_id(task_id)

    if not task or not task.get("is_active"):
        await callback.answer("Bu vazifa endi faol emas!", show_alert=True)
        return

    user_id = callback.from_user.id
    already_done = await db.is_task_completed_by_user(user_id, task_id)

    type_titles = {
        "channel": "📢 Telegram kanalga obuna bo'lish",
        "group": "👥 Telegram guruhga a'zo bo'lish",
        "join_request": "📥 Zayafkali kanalga kirish so'rovi yuborish"
    }
    task_type_text = type_titles.get(task.get("task_type"), "Obuna bo'lish")
    reward = task.get("reward", 0)

    if already_done:
        text = (
            f"✅ <b>{task.get('title')}</b>\n\n"
            f"📌 Turi: {task_type_text}\n"
            f"💰 Mukofot: <b>+{reward:,} UZS</b>\n\n"
            f"<i>Siz bu vazifani allaqachon bajargansiz va mukofotni olgansiz!</i>"
        )
        await callback.message.edit_text(
            text,
            reply_markup=tasks_list_keyboard(await db.get_active_tasks()),
            parse_mode="HTML"
        )
        return

    text = (
        f"📋 <b>Vazifa:</b> {task.get('title')}\n\n"
        f"📌 <b>Shart:</b> {task_type_text}\n"
        f"💵 <b>Mukofot:</b> <b>+{reward:,} UZS</b>\n\n"
        f"<i>Kanalga/guruhga o'ting, obuna bo'ling va 'Vazifani tekshirish' tugmasini bosing!</i>\n\n"
        f"⚠️ <b>Qoida:</b> 30 kun ichida chiqib ketmasligingiz shart (jarima: vazifa narxi + 250 UZS)!"
    )

    await callback.message.edit_text(
        text,
        reply_markup=task_action_keyboard(task.get("url", "https://t.me"), task_id),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("task_check:"))
async def check_single_task(callback: CallbackQuery, bot: Bot):
    task_id = callback.data.split(":")[1]
    task = await db.get_task_by_id(task_id)

    if not task:
        await callback.answer("Vazifa topilmadi!", show_alert=True)
        return

    user_id = callback.from_user.id
    already_done = await db.is_task_completed_by_user(user_id, task_id)
    if already_done:
        await callback.answer("Siz bu vazifani allaqachon bajargansiz!", show_alert=True)
        return

    task_type = task.get("task_type")
    channel_id = task.get("channel_id")
    reward = task.get("reward", 0)

    is_completed = False

    if task_type in ["channel", "group"]:
        if channel_id:
            is_completed = await is_subscribed_to_chat(bot, channel_id, user_id)
    elif task_type == "join_request":
        # Zayavka yuborganini tekshirish
        if channel_id:
            try:
                int_cid = int(channel_id)
                has_req = await db.check_join_request_exists(user_id, int_cid)
                if has_req:
                    is_completed = True
            except Exception:
                pass
            if not is_completed:
                is_completed = await is_subscribed_to_chat(bot, channel_id, user_id)

    if not is_completed:
        await callback.answer(
            "❌ Siz hali vazifani bajarmadingiz!\nIltimos, avval havola orqali a'zo bo'ling yoki so'rov yuboring.",
            show_alert=True
        )
        return

    # Muvaffaqiyatli bajarildi
    await db.complete_task_for_user(user_id, task_id, channel_id, reward)
    await callback.answer("🎉 Tabriklaymiz, vazifa muvaffaqiyatli bajarildi!", show_alert=False)

    text = (
        f"🎉 <b>Tabriklaymiz!</b>\n\n"
        f"Siz '<b>{task.get('title')}</b>' vazifasini muvaffaqiyatli bajardingiz!\n"
        f"Balansingizga <b>+{reward:,} UZS</b> qo'shildi! 💰\n\n"
        f"⚠️ <b>Eslatma:</b> 30 kun ichida a'zolikni bekor qilsangiz, balansingizdan "
        f"<b>{reward + 250:,} UZS</b> (vazifa narxi + 250 UZS) jarima yechib olinadi."
    )

    tasks = await db.get_active_tasks()
    await callback.message.edit_text(text, reply_markup=tasks_list_keyboard(tasks), parse_mode="HTML")
