"""
O'zbekcha va ruscha keng tarqalgan haqoratli/so'kinish so'zlari ro'yxati.
Bu ro'yxat to'liq emas - /addword va /removeword buyruqlari orqali
har bir guruh o'zining qo'shimcha so'zlarini qo'sha oladi.

Diqqat: so'zlar oddiy matn ko'rinishida saqlanadi, lekin tekshiruvda
harflar orasiga qo'yilgan belgilar (masalan "б.л.я", "х_у_й") va lotin-krill
almashtirishlar (masalan "0" -> "o", "3" -> "e") ham hisobga olinadi.
"""

import re

# Asosiy (yadro) so'zlar - o'zak shaklda, keng tarqalgan yozilishlari bilan
BASE_BAD_WORDS = [
    # o'zbekcha
    "jalab", "kotak", "qotoq", "qotaq", "kot", "amma qotoq", "sikish",
    "sikiq", "siktir", "sik", "chuchuk", "kesak", "gandon", "gandon bola",
    "onangni", "onani", "onaxotin", "padar", "padarla'nat", "padarlanat",
    "ahmoq eshak", "eshshak", "eshak", "junjib", "ablah", "qanjiq",
    "iflos", "harom", "kaltak yeg", "sigir emgan", "sigiremgan",
    "bo'q", "boq yegan", "sassiq og'iz",
    # ruscha
    "blyat", "blya", "suka", "pidor", "pidr", "huy", "xuy", "hui",
    "pizda", "pizdec", "pizdets", "ebat", "ebal", "ebu", "eblan",
    "muda", "mudak", "govno", "chmo", "tvar", "svoloch", "kozel",
    "dolbo", "urod", "gnida", "shluha", "shlyuha", "manda",
]


def _normalize(text: str) -> str:
    """Matnni tekshiruv uchun soddalashtiradi: kichik harf, ajratuvchi
    belgilarni olib tashlash, ba'zi harf almashtirishlarni tenglashtirish."""
    text = text.lower()
    # harflar orasiga qo'yilgan nuqta/tire/pastki chiziq/bo'shliq kabi
    # "b.l.y.a" -> "blya" ko'rinishidagi urinishlarni bartaraf etish
    text = re.sub(r"[\s._\-*+]{1,3}(?=[a-zа-яёʻʼ0-9])", "", text)
    replacements = {
        "0": "o", "3": "e", "4": "ch", "1": "i", "@": "a", "$": "s",
        "ё": "e", "й": "i", "щ": "sh", "ц": "s",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def contains_bad_word(text: str, extra_words: list[str] | None = None) -> str | None:
    """Matnda haqoratli so'z topilsa, o'sha so'zni qaytaradi; aks holda None."""
    if not text:
        return None
    normalized = _normalize(text)
    words = list(BASE_BAD_WORDS) + [w.lower() for w in (extra_words or [])]
    for word in words:
        w_norm = _normalize(word)
        if w_norm and w_norm in normalized:
            return word
    return None
