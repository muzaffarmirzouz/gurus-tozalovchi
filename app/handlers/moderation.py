"""Asosiy moderatsiya: so'kinish, link, reklama filtri va
guruhga yozish uchun majburiy kanalga a'zolikni tekshirish."""

from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.exceptions import TelegramBadRequest

from app import database as db
from app.filters.badwords import contains_bad_word
from app.filters.links_ads import has_link, looks_like_ad

router = Router()

# Bitta foydalanuvchi uchun "hozir tekshirilmoqda" holatini takroriy
# xabar yubormaslik uchun oddiy vaqtinchalik keshlash
_recent_subscribe_prompt: dict[tuple[int, int], float] = {}


async def _is_group_admin(message: Message) -> bool:
    if message.from_user is None:
        return False
    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    except TelegramBadRequest:
        return False
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)


async def _is_subscribed(bot, channel: str, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)
    except TelegramBadRequest:
        # Bot kanalga admin qilib qo'shilmagan yoki kanal noto'g'ri bo'lsa
        # xatolik chiqadi - bunday holda tekshiruvni o'tkazib yuboramiz
        # (guruhni butunlay qulflab qo'ymaslik uchun)
        return True


@router.message(F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def moderate_message(message: Message):
    if message.from_user is None or message.from_user.is_bot:
        return

    settings = await db.get_chat_settings(message.chat.id)

    # Adminlarni filtrlardan ozod qilamiz
    if await _is_group_admin(message):
        return

    text = message.text or message.caption or ""

    # 1) Majburiy kanalga a'zolik tekshiruvi
    channel = settings["required_channel"]
    if settings["require_subscribe"] and channel:
        subscribed = await _is_subscribed(message.bot, channel, message.from_user.id)
        if not subscribed:
            try:
                await message.delete()
            except TelegramBadRequest:
                pass

            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

            channel_display = channel if channel.startswith("@") else channel
            link = f"https://t.me/{channel.lstrip('@')}" if not channel.startswith("-100") else None
            kb_buttons = []
            if link:
                kb_buttons.append([InlineKeyboardButton(text="📢 Kanalga o'tish", url=link)])
            kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons) if kb_buttons else None

            warn = await message.answer(
                f"❗️ {message.from_user.mention_html()}, guruhda yozish uchun avval "
                f"kanalimizga a'zo bo'ling, so'ng xabaringizni qayta yuboring.",
                reply_markup=kb,
                parse_mode="HTML",
            )
            return

    # 2) So'kinish filtri
    if settings["filter_swear"] and text:
        extra_words = await db.get_custom_words(message.chat.id)
        bad = contains_bad_word(text, extra_words)
        if bad:
            try:
                await message.delete()
            except TelegramBadRequest:
                pass
            await message.answer(
                f"🚫 {message.from_user.mention_html()}, xabaringizda haqoratli so'z "
                f"borligi sababli o'chirildi.",
                parse_mode="HTML",
            )
            return

    # 3) Reklama filtri (havola + reklama belgilariga qarab)
    if settings["filter_ads"] and text and looks_like_ad(text):
        try:
            await message.delete()
        except TelegramBadRequest:
            pass
        await message.answer(
            f"🚫 {message.from_user.mention_html()}, xabaringiz reklama sifatida "
            f"aniqlanib o'chirildi.",
            parse_mode="HTML",
        )
        return

    # 4) Havola (link) filtri
    if settings["filter_links"] and text and has_link(text):
        try:
            await message.delete()
        except TelegramBadRequest:
            pass
        await message.answer(
            f"🚫 {message.from_user.mention_html()}, guruhda havola (link) "
            f"yuborish taqiqlangan.",
            parse_mode="HTML",
        )
        return
