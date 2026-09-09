"""Botni guruhga qo'shish huquqini cheklash: botni faqat sizning
belgilangan shaxsiy kanalingizga a'zo bo'lgan odamlar o'z guruhiga
qo'sha oladi. Aks holda bot avtomatik o'sha guruhdan chiqib ketadi."""

from aiogram import Router
from aiogram.types import ChatMemberUpdated
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.exceptions import TelegramBadRequest

from app.config import REQUIRED_CHANNEL_DEFAULT

router = Router()


async def _is_subscribed(bot, channel: str, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
    except TelegramBadRequest:
        # Bot kanalga admin qilib qo'shilmagan yoki kanal noto'g'ri bo'lsa,
        # tekshiruvni bloklamaslik uchun o'tkazib yuboramiz
        return True


@router.my_chat_member()
async def on_bot_membership_update(event: ChatMemberUpdated):
    if event.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return

    old = event.old_chat_member
    new = event.new_chat_member

    just_added = (
        old.status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
        and new.status in (ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR)
    )
    if not just_added:
        return

    if not REQUIRED_CHANNEL_DEFAULT:
        return  # global kanal sozlanmagan bo'lsa, tekshiruvsiz ishlayveradi

    adder = event.from_user
    if adder is None:
        return

    subscribed = await _is_subscribed(event.bot, REQUIRED_CHANNEL_DEFAULT, adder.id)
    if subscribed:
        return

    try:
        await event.bot.send_message(
            event.chat.id,
            f"❗️ Botdan foydalanish uchun avval "
            f"{REQUIRED_CHANNEL_DEFAULT} kanaliga a'zo bo'ling, "
            f"so'ng botni qaytadan guruhga qo'shing.",
        )
    except TelegramBadRequest:
        pass

    try:
        await event.bot.leave_chat(event.chat.id)
    except TelegramBadRequest:
        pass
