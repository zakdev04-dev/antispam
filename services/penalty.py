import asyncio
import logging
from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
import database as db
import config

logger = logging.getLogger(__name__)

async def check_penalties_cycle(bot: Bot):
    """
    30 kun ichida bajarilgan vazifalarni tekshirib,
    kanaldan/guruhdan chiqqan foydalanuvchilarga vazifa narxi + 250 UZS jarima qo'llash.
    """
    logger.info("Vazifalar bo'yicha jarimalar tekshiruvi boshlandi...")
    try:
        recent_tasks = await db.get_recent_completed_tasks_for_penalty()
        for rec in recent_tasks:
            user_id = rec["user_id"]
            channel_id = rec.get("channel_id")
            reward = rec.get("reward", 0)
            rec_id = rec["_id"]

            if not channel_id:
                continue

            try:
                member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
                # Agar kanaldan chiqib ketgan yoki haydalgan bo'lsa
                if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                    penalty = reward + config.PENALTY_FEE
                    await db.update_user_balance(user_id, -penalty)
                    await db.mark_task_penalized(rec_id)

                    try:
                        await bot.send_message(
                            chat_id=user_id,
                            text=(
                                f"⚠️ <b>Jarima qo'llandi!</b>\n\n"
                                f"Siz 30 kun ichida vazifa kanalidan/guruhidan chiqib ketganingiz aniqlandi.\n"
                                f"Balansingizdan vazifa narxi ({reward:,} UZS) + 250 UZS jarima "
                                f"(jami <b>-{penalty:,} UZS</b>) yechib olindi!\n\n"
                                f"<i>Iltimos, vazifa shartlariga qat'iy rioya qiling!</i>"
                            ),
                            parse_mode="HTML"
                        )
                    except TelegramForbiddenError:
                        await db.update_user_status(user_id, False)
                    except Exception as e:
                        logger.warning(f"Foydalanuvchiga jarima xabarini yuborib bo'lmadi ({user_id}): {e}")

            except TelegramBadRequest as e:
                # Bot kanaldan chiqarilgan yoki kanal topilmadi
                logger.warning(f"Kanalni tekshirib bo'lmadi ({channel_id}): {e}")
            except Exception as e:
                logger.error(f"Jarima tekshiruvida xatolik (user: {user_id}, task: {rec_id}): {e}")

    except Exception as e:
        logger.error(f"check_penalties_cycle xatoligi: {e}")

async def penalty_background_worker(bot: Bot, interval_seconds: int = 3600):
    """Orqa fonda har 1 soatda avtomatik tekshirib turish."""
    while True:
        await check_penalties_cycle(bot)
        await asyncio.sleep(interval_seconds)
