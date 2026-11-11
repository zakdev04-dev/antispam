import logging
from aiogram import Router
from aiogram.types import ChatJoinRequest, ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

import database as db

router = Router()
logger = logging.getLogger(__name__)

# --- CHAT JOIN REQUEST (ZAYAVKALARNI TUTIB QOLISH) ---
@router.chat_join_request()
async def handle_chat_join_request(event: ChatJoinRequest):
    """
    Foydalanuvchi kanalda 'kirish so'rovi' (join request) yuborganida
    avtomatik tarzda bazaga saqlanadi.
    """
    user_id = event.from_user.id
    chat_id = event.chat.id
    try:
        await db.save_join_request(user_id=user_id, channel_id=chat_id)
        logger.info(f"Yangi zayavka saqlandi: user_id={user_id}, chat_id={chat_id}")
    except Exception as e:
        logger.error(f"Zayavkani saqlashda xatolik: {e}")

# --- BOT BLOKLANGANLIGINI KUZATISH ---
@router.my_chat_member()
async def handle_bot_status_change(event: ChatMemberUpdated):
    """
    Foydalanuvchi botni bloklasa yoki qayta yoqsa, statusini yangilash.
    """
    user_id = event.from_user.id
    new_status = event.new_chat_member.status

    if new_status in [ChatMemberStatus.KICKED, ChatMemberStatus.LEFT]:
        await db.update_user_status(user_id, False)
        logger.info(f"Foydalanuvchi botni to'xtatdi/blokladi: {user_id}")
    elif new_status == ChatMemberStatus.MEMBER:
        await db.update_user_status(user_id, True)
        logger.info(f"Foydalanuvchi botni qayta faollashtirdi: {user_id}")
