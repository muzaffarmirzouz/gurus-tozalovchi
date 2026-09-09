"""Guruhga yangi bot qo'shilganda uni tekshirish: agar u ruxsat etilgan
(allowlist) ro'yxatda bo'lmasa - avtomatik chiqarib yuboriladi.
Shu bilan begona reklama-bot yoki spam-botlar guruhga kira olmaydi."""

from aiogram import Router, F
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus

from app import database as db

router = Router()


@router.chat_member()
async def on_chat_member_update(event: ChatMemberUpdated):
    chat = event.chat
    new = event.new_chat_member
    old = event.old_chat_member

    # Faqat "kimdir a'zo bo'ldi" holatini qiziqtiramiz
    if old.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED) and new.status == ChatMemberStatus.MEMBER:
        user = new.user
        if not user.is_bot:
            return

        settings = await db.get_chat_settings(chat.id)
        if not settings["block_bots"]:
            return

        if await db.is_bot_allowed(chat.id, user.id):
            return

        # Bizning o'z botimizni chiqarib yubormaslik uchun tekshiruv
        me = await event.bot.get_me()
        if user.id == me.id:
            return

        try:
            await event.bot.ban_chat_member(chat.id, user.id)
            await event.bot.unban_chat_member(chat.id, user.id)  # kick, taqiqlamaslik
            await event.bot.send_message(
                chat.id,
                f"🤖 Noma'lum bot ({user.full_name}) guruhdan chiqarib yuborildi.\n"
                f"Botni ruxsat berish uchun admin: /allowbot {user.id}",
            )
        except Exception:
            pass
