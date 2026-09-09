# TozalovchiBOT

Telegram guruhlarni tozalovchi moderatsiya bot:

- 🚫 So'kinish/haqoratli so'zlarni avtomatik o'chiradi (o'zbek + rus)
- 🔗 Havolalarni (linklarni) o'chiradi
- 📢 Reklama xabarlarini aniqlab o'chiradi
- 🤖 Ruxsatsiz botlar guruhga qo'shilsa avtomatik chiqarib yuboradi
- 📌 Foydalanuvchi belgilangan shaxsiy kanalga a'zo bo'lmaguncha guruhda yoza olmaydi (majburiy obuna)
- Guruh adminlari filtrlardan ozod

Har bir guruh o'z sozlamalariga ega (bitta bot bir nechta guruhda ishlay oladi).

## 1. Bot yaratish

1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing.
2. `/newbot` buyrug'ini yuboring, nom va username bering.
3. Sizga beriladigan **tokenni** saqlab qo'ying.
4. `/setjoingroups` va guruh sozlamalarini yoqing (odatda default yoqilgan).
5. Botning **Group Privacy** rejimini o'chiring: BotFather → botingiz →
   `Bot Settings` → `Group Privacy` → `Turn off`.
   (Aks holda bot guruhdagi barcha xabarlarni ko'ra olmaydi.)

## 2. Sozlash

`.env.example` faylini `.env` deb nusxalang va to'ldiring:

```
BOT_TOKEN=BotFather'dan olingan token
REQUIRED_CHANNEL=@sizning_shaxsiy_kanalingiz
OWNER_ID=sizning_telegram_id'ingiz
DB_PATH=bot.db
```

`REQUIRED_CHANNEL`ni keyinroq guruh ichida `/setchannel @kanal` buyrug'i
bilan ham o'rnatish/o'zgartirish mumkin.

## 3. Botni guruhga va kanalga qo'shish

1. Botni guruhingizga qo'shing va **admin** qiling. Kamida quyidagi
   huquqlarni bering:
   - Xabarlarni o'chirish (Delete messages)
   - Foydalanuvchilarni bloklash (Ban users)
2. Botni majburiy a'zolik talab qilinadigan **shaxsiy kanalingizga** ham
   qo'shing va **admin** qiling (kamida "a'zolarni ko'rish" huquqi
   yetarli). Bu bosqichsiz majburiy obuna tekshiruvi ishlamaydi.

## 4. Ishga tushirish (lokal)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.bot
```

## 5. Railway'ga joylashtirish

1. Ushbu papkani GitHub repository sifatida yuklang.
2. [Railway](https://railway.app) da yangi loyiha yarating → "Deploy from
   GitHub repo" → shu repo'ni tanlang.
3. Railway "Variables" bo'limida quyidagilarni kiriting:
   - `BOT_TOKEN`
   - `REQUIRED_CHANNEL`
   - `OWNER_ID`
   - `DB_PATH` = `/data/bot.db` (agar Volume ulasangiz)
4. Ma'lumotlar bazasi qayta deploy'larda o'chib ketmasligi uchun Railway
   "Volumes" bo'limidan Volume qo'shing va uni `/data` ga mount qiling,
   `DB_PATH=/data/bot.db` qilib qo'ying.
5. Railway avtomatik `Procfile`dagi `worker: python -m app.bot`
   buyrug'ini ishga tushiradi.

## 6. Guruhda sozlash buyruqlari (faqat adminlar uchun)

| Buyruq | Vazifasi |
|---|---|
| `/setchannel @kanal` | Majburiy a'zolik kanalini belgilaydi |
| `/unsetchannel` | Majburiy a'zolikni bekor qiladi |
| `/settings` | Joriy sozlamalarni ko'rsatadi |
| `/toggle swear\|links\|ads\|bots\|subscribe` | Tegishli filtrni yoqadi/o'chiradi |
| `/addword so'z` | Qo'shimcha taqiqlangan so'z qo'shadi |
| `/removeword so'z` | So'zni ro'yxatdan o'chiradi |
| `/allowbot <bot_id>` | Ma'lum botga guruhda qolishga ruxsat beradi |

## Eslatmalar

- So'kinish so'zlari ro'yxati `app/filters/badwords.py` faylida —
  xohlagancha kengaytirish mumkin, yoki `/addword` orqali guruh ichidan.
- Reklama aniqlash kalit so'zlari `app/filters/links_ads.py` da.
- Bot faqat guruh a'zolarining xabarlarini tekshiradi; guruh adminlari
  va bot egasi filtrlardan ozod.
