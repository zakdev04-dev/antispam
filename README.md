# 🚀 Anti Spam & Daromad Telegram Bot

Ushbu loyiha **Python (Aiogram 3)** va **MongoDB (Motor)** asosida ishlab chiqilgan, barcha ilg'or imkoniyatlarga ega Telegram bot hisoblanadi. Bot **Render.com** platformasida (Web Service rejimida port binding bilan) hamda oddiy serverlarda mukammal ishlashga to'liq moslashtirilgan.

---

## 🌟 Botning Asosiy Funksiyalari

### 1. Foydalanuvchi Oqimi (User Flow)
* **Start va Kontakt yuborish**: Foydalanuvchi `/start` bosganida bot salomlashadi va xavfsizlik / haqiqiylikni ta'minlash uchun telefon raqamini (kontakt) ulashishni so'raydi (`📱 Kontaktni ulashish` tugmasi).
* **Majburiy Obuna Tizimi**:
  * Ochiq kanallar (`@username`).
  * Shaxsiy (Private) kanallar.
  * Zayafkali kanallar (`Join Request` — kirish so'rovi yuborilganini tekshiradi).
  * Tashqi havolalar (Web linklar).
  * **Dinamik obuna**: Foydalanuvchi obuna bo'lgan kanallar ro'yxatdan avtomatik yo'qoladi, faqat hali obuna bo'lmaganlari ko'rinadi!
  * Tugmalar nomi har doim talabga binoan: `< Obuna bo'lish >`.
* **Foydalanuvchi Interfeysi**:
  ```
  [ 📹 Video qo'llanma ]
  [ 👤 Kabinet ]  [ 🔗 Taklif havola ]
  [ 📢 Reklama ]  [ ℹ️ Bot haqida ]
  [ 🆘 Yordam ]
  ```
* **📹 Video qo'llanma bo'limi**:
  * Admin yuklagan video qo'llanmani olish bo'limi.
  * Tugma bosilganda foydalanuvchi hisobida kamida **15 000 UZS** bo'lishi tekshiriladi.
  * Mablag' yetarli bo'lsa, balansidan 15 000 UZS yechib olinadi va maxsus video qo'llanma yuboriladi.
  * Yetarli bo'lmasa, ogohlantirish va `💳 Hisobni to'ldirish` tugmasi chiqadi.
* **👤 Kabinet bo'limi**:
  * Ma'lumotlar: Ism, username, Telegram ID, telefon raqami, hisob (balans UZS da), botga qo'shilgan sana va vaqti.
  * Pastida inline tugmalar: `💳 Hisobni to'ldirish` va `📋 Vazifalar`.
* **💳 Hisobni to'ldirish**:
  * Foydalanuvchidan summa so'raladi (masalan: `20000`).
  * Admin kiritgan karta raqami va egasining ismi ko'rsatiladi:
    `Hurmatli [Ism], siz admin kiritgan karta: [Karta], kiritilgan summa: [Summa] UZS, to'ldiring va to'lov chekini yuboring.`
  * Foydalanuvchi chek (skrinshot yoki kvitansiya) yuboradi.
  * Adminga darhol xabar boradi: chek rasmi, ma'lumotlar, `✅ Tasdiqlash` va `❌ Bekor qilish` tugmalari.
  * Admin tasdiqlasa balansga qo'shiladi va foydalanuvchiga xushxabar boradi; bekor qilsa rad etilgani bildiriladi.
* **📋 Vazifalar va 30 kunlik jarima tizimi**:
  * Admin kiritgan vazifalar (Telegram kanal, guruh, zayafkali kanal).
  * Bajarilganda admin belgilagan narx foydalanuvchi balansiga qo'shiladi.
  * **30 kunlik qoida**: Agar foydalanuvchi 30 kun ichida kanaldan yoki guruhdan chiqib ketsa, uning balansidan **vazifa narxi + 250 UZS** jarima sifatida avtomatik yechib olinadi (Orqa fonda ishlovchi tekshiruvchi orqali).
* **🔗 Taklif havola (Referal)**:
  * Do'stlarni taklif qilish orqali pul ishlash.
  * Kreativ reklama posti va `📤 Do'stlarga ulashish` tugmasi.
  * Taklif qilingan do'st kontaktini berib, majburiy kanallarga a'zo bo'lgach, taklif qilganga admin belgilagan summa beriladi.
* **📢 Reklama**: Admin joylagan reklama posti (tugmali yoki tugmasiz).
* **ℹ️ Bot haqida**: Bot afzalliklari va ma'lumotlar.
* **🆘 Yordam**: Adminga murojaat va yordam kontaktlari.

---

### 2. Admin Paneli (`/admin`)
Faqat `.env` dagi `ADMINS` ro'yxatidagi ID larga ruxsat beriladi:
* **📢 Kanal ulash**: Majburiy kanallar qo'shish (Ochiq, Shaxsiy, Zayafkali, Tashqi havola).
* **⚙️ Kanallarni boshqarish**: Ulangan kanallarni ko'rish va o'chirish.
* **📊 Statistika**:
  * Jami foydalanuvchilar soni.
  * Faol (Active) foydalanuvchilar.
  * Bloklagan foydalanuvchilar.
  * Bugun qo'shilganlar soni.
  * Ulangan majburiy kanallar soni.
  * Faol vazifalar soni.
* **📹 Video joylash**: Foydalanuvchilar 15 000 UZS ga yuklab oladigan videoni o'rnatish.
* **✉️ Xabar yuborish (Rassilka)**:
  * Barcha foydalanuvchilarga matn, rasm, video yuborish.
  * Tugmali (URL button) yoki tugmasiz rejim.
  * Yetkazilganlar va bloklaganlar hisoboti.
* **📢 Reklama joylash**: Reklama bo'limi postini o'rnatish (tugmali yoki tugmasiz).
* **📋 Vazifa qo'shish**: Yangi kanal/guruh vazifasi qo'shish va alohida mukofot narxini belgilash.
* **🗂 Vazifalarni boshqarish**: Vazifalarni o'chirish.
* **💰 Referal narxi**: Yangi narx belgilash.
* **💵 Vazifa narxi**: Standart vazifa narxini sozlash.
* **💳 Karta ma'lumotlari**: To'lov qabul qilinadigan karta raqami va egasini kiritish.
* **ℹ️ Bot haqida matni**: Ma'lumot matnini tahrirlash.
* **🆘 Yordam matni**: Aloqa matnini tahrirlash.

---

## 🛠 O'rnatish va Ishga tushirish (Local)

### 1. Talablar:
* Python 3.10 yoki undan yuqori
* MongoDB (Local yoki [MongoDB Atlas](https://www.mongodb.com/cloud/atlas))

### 2. Loyihani sozlash:
```bash
# Virtual muhit yaratish
python -m venv venv

# Virtual muhitni faollashtirish (Windows)
.\venv\Scripts\activate
# (Linux / Mac): source venv/bin/activate

# Kutubxonalarni o'rnatish
pip install -r requirements.txt
```

### 3. `.env` faylini to'ldirish:
`.env.example` faylidan nusxa olib `.env` nomli fayl yarating:
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
MONGO_URI=mongodb+srv://user:password@cluster0.mongodb.net/anti_spam_bot?retryWrites=true&w=majority
ADMINS=123456789,987654321
PORT=8080
VIDEO_PRICE=15000
PENALTY_FEE=250
```

### 4. Botni ishga tushirish:
```bash
python main.py
```

---

## 🌐 Render.com ga Deploy Qilish (Bosqichma-bosqich)

1. Loyihani **GitHub** repozitoriyangizga yuklang (`git push origin main`).
2. [Render.com](https://render.com) saytiga kiring va **New +** tugmasini bosib **Web Service** ni tanlang.
3. GitHub repozitoriyangizni ulang.
4. Quyidagi parametrlarni kiriting:
   * **Name**: `anti-spam-bot`
   * **Language**: `Python 3`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `python main.py`
5. **Environment Variables** (Muhit o'zgaruvchilari) bo'limida quyidagilarni kiriting:
   * `BOT_TOKEN` = BotFather dan olingan token
   * `MONGO_URI` = MongoDB Atlas ulanish havolasi
   * `ADMINS` = Telegram ID laringiz (masalan: `123456789`)
   * `PORT` = `10000` (Render buni avtomatik o'rnatadi)
6. **Create Web Service** tugmasini bosing!
7. Render bir necha daqiqada kutubxonalarni o'rnatib, Health Check portini (`/health`) ochadi va bot 24/7 rejimida uzluksiz ishlay boshlaydi!

---

## 📁 Loyiha Strukturasi

```
anti spma/
│
├── config.py                 # Konfiguratsiya va muhit o'zgaruvchilari
├── database.py               # MongoDB asinxron ulanishi va querylar
├── main.py                   # Bot kirish nuqtasi, Health Check va Background Worker
├── requirements.txt          # Python kutubxonalari
├── Procfile                  # Render.com start konfiguratsiyasi
├── render.yaml               # Render blueprint
├── .env.example              # Namuna konfiguratsiya
├── .gitignore                # Git e'tiborsiz qoldiradigan fayllar
├── README.md                 # Qo'llanma
│
├── filters/
│   └── admin.py              # Faqat adminlar uchun filtr
│
├── keyboards/
│   ├── default.py            # Kontakt va Asosiy menyu
│   ├── inline.py             # Majburiy obuna, Kabinet, Vazifalar, Referal
│   └── admin_kb.py           # Admin panelining barcha klaviaturalari
│
├── handlers/
│   ├── start.py              # /start, telefon raqam qabul qilish, obuna tekshiruvi
│   ├── user_menu.py          # Video qo'llanma, Kabinet, Reklama, Bot haqida, Yordam
│   ├── payment.py            # Hisob to'ldirish, chek qabul qilish, admin tasdiqlashi
│   ├── tasks.py              # Vazifalar va tekshirish
│   ├── admin.py              # Admin paneli va Statistika
│   ├── admin_channels.py     # Kanallarni ulash (4 xil tur) va boshqarish
│   ├── admin_tasks.py        # Vazifalar yaratish va o'chirish
│   ├── admin_broadcast.py    # Foydalanuvchilarga xabar yuborish (tugmali/tugmasiz)
│   ├── admin_settings.py     # Narxlar, karta, video va matnlarni sozlash
│   └── events.py             # Zayavkalar (JoinRequest) va bloklashlarni kuzatish
│
├── services/
│   ├── checker.py            # Obunani dinamik tekshiruvchi (a'zo bo'lganlar yashiriladi)
│   └── penalty.py            # 30 kun ichida chiqqanlarga vazifa narxi + 250 UZS jarima yechish
│
└── states/
    ├── user_states.py        # To'lov holatlari
    └── admin_states.py       # Admin FSM holatlari
```
