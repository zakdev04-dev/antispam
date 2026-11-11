# 🚀 Anti Spam & Daromad Telegram Boti (Node.js & MongoDB)

Ushbu loyiha **JavaScript (Node.js, Telegraf v4)** va **MongoDB (Mongoose)** asosida to'liq ishlab chiqilgan. Bot **Render.com** platformasida (Web Service rejimida port binding bilan) hamda oddiy serverlarda 24/7 rejimida uzluksiz ishlashga to'liq moslashtirilgan.

---

## 🌟 Botning Asosiy Funksiyalari

### 1. Foydalanuvchi Oqimi (User Flow)
* **Start va Kontakt yuborish**: Foydalanuvchi `/start` bosganida bot salomlashadi va telefon raqamini ulashishni so'raydi (`📱 Kontaktni ulashish` tugmasi).
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
  * Tugma bosilganda hisobida kamida **15 000 UZS** bo'lishi tekshiriladi.
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
  * **30 kunlik qoida**: Agar foydalanuvchi 30 kun ichida kanaldan yoki guruhdan chiqib ketsa, uning balansidan **vazifa narxi + 250 UZS** jarima sifatida avtomatik yechib olinadi (Orqa fonda har soatda tekshiruvchi orqali).
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
* **📊 Statistika**: Jami foydalanuvchilar, Faol foydalanuvchilar, Bloklaganlar, Bugun qo'shilganlar, Ulangan kanallar va Faol vazifalar soni.
* **📹 Video joylash**: 15 000 UZS lik videoni o'rnatish.
* **✉️ Xabar yuborish (Rassilka)**: Barcha foydalanuvchilarga matn, rasm, video yuborish (tugmali yoki tugmasiz).
* **📢 Reklama joylash**: Reklama bo'limi postini o'rnatish.
* **📋 Vazifa qo'shish**: Yangi kanal/guruh vazifasi qo'shish va alohida mukofot narxini belgilash.
* **🗂 Vazifalarni boshqarish**: Vazifalarni o'chirish.
* **💰 Referal narxi**: Yangi referal narxini sozlash.
* **💵 Vazifa narxi**: Standart vazifa narxini sozlash.
* **💳 Karta ma'lumotlari**: Karta raqami va egasini kiritish.
* **ℹ️ Bot haqida matni**: Ma'lumot matnini tahrirlash.
* **🆘 Yordam matni**: Aloqa matnini tahrirlash.

---

## 🛠 O'rnatish va Ishga tushirish (Local)

### 1. Talablar:
* Node.js v18 yoki undan yuqori
* MongoDB (Local yoki MongoDB Atlas)

### 2. Kutubxonalarni o'rnatish:
```bash
npm install
```

### 3. `.env` faylini to'ldirish:
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
npm start
```

---

## 🌐 Render.com ga Deploy Qilish

1. Loyihani GitHub ga push qiling.
2. Render.com da **New + -> Web Service** ni tanlang.
3. Repozitoriyangizni ulang.
4. Sozlamalar:
   - **Environment**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `node index.js`
5. **Environment Variables**:
   - `BOT_TOKEN`
   - `MONGO_URI`
   - `ADMINS`
   - `PORT` = `10000`
6. **Create Web Service** bosing.
