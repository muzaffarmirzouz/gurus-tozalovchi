"""Xabar ichida telefon raqami bor-yo'qligini aniqlaydi.

Turli formatlarni qamrab oladi: +998901234567, 998 90 123 45 67,
90-123-45-67, (90) 123 45 67 va h.k. Belgilar orasidagi bo'shliq,
tire, qavs va nuqtalarni hisobga oladi.
"""

import re

# Kamida 7 ta raqamdan iborat, orasida bo'shliq/tire/qavs/nuqta bo'lishi
# mumkin bo'lgan ketma-ketlikni qidiradi (ixtiyoriy "+" bilan boshlanadi)
_PHONE_RE = re.compile(r"(\+?\d[\d\-\s\(\)\.]{5,}\d)")


def has_phone_number(text: str) -> bool:
    if not text:
        return False
    for match in _PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group())
        # Odatiy telefon raqamlari 7-15 ta raqamdan iborat bo'ladi
        # (juda qisqa sonlarni - masalan sana yoki narxni - filtrlamaslik uchun)
        if 7 <= len(digits) <= 15:
            return True
    return False
