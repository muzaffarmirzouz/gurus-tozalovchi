import re

URL_RE = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|[a-z0-9\-]+\.(com|net|org|uz|ru|io|shop|store|xyz|site|online|club|biz)\b)",
    re.IGNORECASE,
)

MENTION_RE = re.compile(r"@[a-zA-Z0-9_]{4,}")

# Reklama/spamga xos kalit so'zlar (o'zbek/rus)
AD_KEYWORDS = [
    "reklama", "sotiladi", "sotib oling", "sotib olish", "chegirma",
    "aksiya", "buyurtma", "bepul", "faqat bugun", "shoshiling",
    "kanalga o'ting", "kanalga qo'shiling", "obuna bo'ling",
    "заработ", "подпишись", "подписывайся", "скидка", "акция",
    "бесплатно", "казино", "casino", "ставки", "ставка", "1xbet",
    "crypto", "kripto", "investitsiya", "investitsiya qiling",
    "работа на дому", "удаленная работа", "доход от",
    # 18+ / intim xizmat reklamasi (soxta profillar orqali tarqatiladigan spam)
    "18+", "интим", "интим услуги", "индивидуалка", "индивидуалки",
    "проститутки", "путана", "путаны", "vip xizmat", "vip usluga",
    "eskort xizmati", "escort", "досуг", "снять девушку", "интимные услуги",
    "intim xizmat", "yolg'iz ayollar", "мои услуги", "приватные видео",
    "приват видео", "webcam", "вебкам", "onlyfans",
]


def has_link(text: str) -> bool:
    if not text:
        return False
    return bool(URL_RE.search(text))


def has_mention(text: str) -> bool:
    if not text:
        return False
    return bool(MENTION_RE.search(text))


def looks_like_ad(text: str) -> bool:
    if not text:
        return False
    low = text.lower()
    if any(kw in low for kw in AD_KEYWORDS):
        return True
    # Ko'p sonli link/mention + qisqa matn - odatda spam/reklama belgisi
    if (has_link(text) or has_mention(text)) and len(text) < 200:
        link_count = len(URL_RE.findall(text)) + len(MENTION_RE.findall(text))
        if link_count >= 2:
            return True
    return False
