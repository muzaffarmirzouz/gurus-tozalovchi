"""Guruhga a'zo qo'shilgani/chiqib ketgani haqidagi tizim xabarlarini
(masalan "Ali guruhga qo'shildi", "Vali guruhdan chiqdi") guruh
a'zolaridan yashirish uchun avtomatik o'chiradi."""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

router = Router()


@router.message(F.new_chat_members)
async def hide_join_message(message: Message):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass


@router.message(F.left_chat_member)
async def hide_left_message(message: Message):
    try:
        await message.delete()
    except TelegramBadRequest:
        pass
