import logging
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
import database as db

logger = logging.getLogger(__name__)

async def is_subscribed_to_chat(bot: Bot, chat_id: int | str, user_id: int) -> bool:
    """Chat a'zoligini tekshirish."""
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        if member.status in [
            ChatMemberStatus.CREATOR,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.RESTRICTED
        ]:
            return True
        return False
    except Exception as e:
        logger.warning(f"Kanal a'zoligini tekshirishda xatolik ({chat_id}): {e}")
        return False

async def get_unsubscribed_channels(bot: Bot, user_id: int) -> list:
    """
    Foydalanuvchi obuna bo'lmagan kanallar ro'yxatini qaytaradi.
    Obuna bo'lgan kanallar ro'yxatdan chiqarib tashlanadi (ko'rinmay qoladi).
    """
    all_channels = await db.get_channels()
    if not all_channels:
        return []

    user = await db.get_user(user_id)
    external_clicks = user.get("subscribed_external_links", []) if user else []

    unsubscribed = []

    for ch in all_channels:
        ch_type = ch.get("type")
        ch_id = ch.get("channel_id")
        str_id = str(ch["_id"])

        if ch_type in ["public", "private"]:
            # Bot orqali chat a'zoligini tekshirish
            if ch_id:
                is_sub = await is_subscribed_to_chat(bot, ch_id, user_id)
                if not is_sub:
                    unsubscribed.append(ch)
            else:
                unsubscribed.append(ch)

        elif ch_type == "join_request":
            # Zayavka yuborganini tekshirish
            has_requested = False
            if ch_id:
                try:
                    int_chat_id = int(ch_id)
                    has_requested = await db.check_join_request_exists(user_id, int_chat_id)
                except Exception:
                    pass

                # Agar zayavka bo'lsa yoki allaqachon a'zo bo'lsa
                if not has_requested:
                    is_sub = await is_subscribed_to_chat(bot, ch_id, user_id)
                    if not is_sub:
                        unsubscribed.append(ch)
            else:
                unsubscribed.append(ch)

        elif ch_type == "external":
            # Tashqi havolaga bosganligini tekshirish
            if str_id not in external_clicks:
                unsubscribed.append(ch)

    return unsubscribed
