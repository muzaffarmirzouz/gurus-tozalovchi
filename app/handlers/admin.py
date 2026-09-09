"""Guruh adminlari uchun sozlash buyruqlari."""

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.exceptions import TelegramBadRequest

from app import database as db

router = Router()


async def _require_admin(message: Message) -> bool:
    # Guruh nomidan (anonim admin sifatida) yozilgan xabar - Telegram bunday
    # xabarlarni sender_chat = guruhning o'zi qilib yuboradi, from_user esa
    # haqiqiy odam emas, maxsus "GroupAnonymousBot" bo'ladi. Bunday xabar
    # faqat admin tomonidan yuborilishi mumkin, shuning uchun avtomatik ruxsat.
    if message.sender_chat is not None and message.sender_chat.id == message.chat.id:
        return True

    if message.from_user is None:
        return False

    try:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
    except TelegramBadRequest:
        await message.answer(
            "Adminligingizni tekshirib bo'lmadi. Iltimos, birozdan so'ng qayta urinib ko'ring."
        )
        return False

    if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
        await message.answer("Bu buyruqni faqat guruh adminlari ishlata oladi.")
        return False
    return True


@router.message(Command("start"), F.chat.type == ChatType.PRIVATE)
async def cmd_start(message: Message):
    await message.answer(
        "Salom! Men guruh tozalovchi botiman.\n\n"
        "Meni guruhingizga ADMIN qilib qo'shing (xabarlarni o'chirish va "
        "a'zolarni chiqarish huquqi bilan), so'ng guruh ichida quyidagi "
        "buyruqlar bilan sozlang:\n\n"
        "/setchannel @kanal - majburiy a'zolik kanalini belgilash\n"
        "/unsetchannel - majburiy a'zolikni o'chirish\n"
        "/settings - joriy sozlamalarni ko'rish\n"
        "/toggle swear|links|ads|bots|subscribe - filtrni yoqish/o'chirish\n"
        "/addword so'z1, so'z2 - qo'shimcha taqiqlangan so'z(lar) qo'shish\n"
        "/removeword so'z1, so'z2 - so'z(lar)ni ro'yxatdan o'chirish\n"
        "/listwords - qo'shimcha so'zlar ro'yxatini ko'rish\n"
        "/allowbot bot_id - ma'lum botga guruhda qolishga ruxsat berish\n\n"
        "Diqqat: majburiy a'zolik ishlashi uchun meni kanalingizga ham "
        "ADMIN qilib qo'shishingiz kerak."
    )


@router.message(Command("settings"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_settings(message: Message):
    if not await _require_admin(message):
        return
    s = await db.get_chat_settings(message.chat.id)
    words = await db.get_custom_words(message.chat.id)

    def flag(v: bool) -> str:
        return "✅ yoqilgan" if v else "❌ o'chirilgan"

    await message.answer(
        "⚙️ Joriy sozlamalar:\n"
        f"Majburiy kanal: {s['required_channel'] or 'belgilanmagan'}\n"
        f"— majburiy a'zolik: {flag(s['require_subscribe'])}\n"
        f"So'kinish filtri: {flag(s['filter_swear'])}\n"
        f"Havola (link) filtri: {flag(s['filter_links'])}\n"
        f"Reklama filtri: {flag(s['filter_ads'])}\n"
        f"Begona botlarni bloklash: {flag(s['block_bots'])}\n"
        f"Qo'shimcha taqiqlangan so'zlar soni: {len(words)}"
    )


@router.message(Command("setchannel"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_setchannel(message: Message, command: CommandObject):
    if not await _require_admin(message):
        return
    if not command.args:
        await message.answer("Foydalanish: /setchannel @kanal_username")
        return
    channel = command.args.strip()
    await db.set_required_channel(message.chat.id, channel)
    await message.answer(
        f"✅ Majburiy a'zolik kanali {channel} qilib belgilandi.\n"
        f"Eslatma: botni shu kanalga ADMIN qilib qo'shishni unutmang, "
        f"aks holda a'zolik tekshiruvi ishlamaydi."
    )


@router.message(Command("unsetchannel"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_unsetchannel(message: Message):
    if not await _require_admin(message):
        return
    await db.set_required_channel(message.chat.id, None)
    await message.answer("✅ Majburiy a'zolik kanali o'chirildi.")


_TOGGLE_MAP = {
    "swear": "filter_swear",
    "links": "filter_links",
    "ads": "filter_ads",
    "bots": "block_bots",
    "subscribe": "require_subscribe",
}


@router.message(Command("toggle"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_toggle(message: Message, command: CommandObject):
    if not await _require_admin(message):
        return
    arg = (command.args or "").strip().lower()
    if arg not in _TOGGLE_MAP:
        await message.answer(
            "Foydalanish: /toggle swear|links|ads|bots|subscribe\n"
            "Masalan: /toggle links"
        )
        return
    field = _TOGGLE_MAP[arg]
    current = await db.get_chat_settings(message.chat.id)
    new_value = not current[field]
    await db.toggle_setting(message.chat.id, field, new_value)
    await message.answer(f"{arg}: {'✅ yoqildi' if new_value else '❌ o‘chirildi'}")


def _split_words(raw: str) -> list[str]:
    """So'zlarni vergul yoki qator (yangi satr) bilan ajratib beradi,
    bo'sh elementlarni tashlab yuboradi. Vergul yo'q bo'lsa butun matnni
    bitta ibora sifatida qaytaradi (masalan ko'p so'zli haqorat)."""
    raw = raw.strip()
    if "," in raw or "\n" in raw:
        parts = raw.replace("\n", ",").split(",")
        return [p.strip() for p in parts if p.strip()]
    return [raw] if raw else []


@router.message(Command("addword"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_addword(message: Message, command: CommandObject):
    if not await _require_admin(message):
        return
    if not command.args:
        await message.answer(
            "Foydalanish: /addword so'z\n"
            "Bir nechtasini qo'shish uchun vergul bilan ajrating:\n"
            "/addword so'z1, so'z2, so'z3"
        )
        return
    words = _split_words(command.args)
    if not words:
        await message.answer("Hech qanday so'z topilmadi.")
        return
    for w in words:
        await db.add_custom_word(message.chat.id, w)
    if len(words) == 1:
        await message.answer(f"✅ So'z qo'shildi: {words[0]}")
    else:
        await message.answer(f"✅ {len(words)} ta so'z qo'shildi:\n" + ", ".join(words))


@router.message(Command("removeword"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_removeword(message: Message, command: CommandObject):
    if not await _require_admin(message):
        return
    if not command.args:
        await message.answer(
            "Foydalanish: /removeword so'z\n"
            "Bir nechtasini o'chirish uchun vergul bilan ajrating:\n"
            "/removeword so'z1, so'z2"
        )
        return
    words = _split_words(command.args)
    if not words:
        await message.answer("Hech qanday so'z topilmadi.")
        return
    for w in words:
        await db.remove_custom_word(message.chat.id, w)
    if len(words) == 1:
        await message.answer(f"✅ So'z o'chirildi: {words[0]}")
    else:
        await message.answer(f"✅ {len(words)} ta so'z ro'yxatdan o'chirildi:\n" + ", ".join(words))


@router.message(Command("listwords"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_listwords(message: Message):
    if not await _require_admin(message):
        return
    words = await db.get_custom_words(message.chat.id)
    if not words:
        await message.answer("Qo'shimcha taqiqlangan so'zlar hali qo'shilmagan.")
        return
    await message.answer("📝 Qo'shimcha taqiqlangan so'zlar:\n" + ", ".join(words))


@router.message(Command("allowbot"), F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def cmd_allowbot(message: Message, command: CommandObject):
    if not await _require_admin(message):
        return
    if not command.args or not command.args.strip().isdigit():
        await message.answer("Foydalanish: /allowbot <bot_id>")
        return
    bot_id = int(command.args.strip())
    await db.allow_bot(message.chat.id, bot_id)
    await message.answer(f"✅ Bot ID {bot_id} endi guruhda qolishiga ruxsat berildi.")
