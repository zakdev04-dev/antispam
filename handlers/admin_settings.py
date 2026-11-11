import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import database as db
from filters.admin import IsAdmin
from states.admin_states import (
    SetReferralPriceState, SetTaskPriceState, SetCardState,
    SetVideoGuideState, SetAdPostState, SetAboutTextState, SetHelpTextState
)
from keyboards.admin_kb import admin_main_keyboard
from keyboards.default import cancel_keyboard, yes_no_keyboard
from keyboards.inline import custom_ad_keyboard

router = Router()
router.message.filter(IsAdmin())

logger = logging.getLogger(__name__)

# --- REFERAL NARXI ---
@router.message(F.text == "💰 Referal narxi")
async def start_set_ref_price(message: Message, state: FSMContext):
    current = await db.get_setting("referral_price") or 1000
    await state.set_state(SetReferralPriceState.waiting_for_price)
    await message.answer(
        f"💰 <b>Referal narxini sozlash</b>\n\n"
        f"Hozirgi narx: <b>{current:,} UZS</b>\n\n"
        f"Yangi narxni so'mda (raqam bilan) kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetReferralPriceState.waiting_for_price, F.text == "❌ Bekor qilish")
async def cancel_set_ref_price(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetReferralPriceState.waiting_for_price)
async def process_set_ref_price(message: Message, state: FSMContext):
    text = message.text.replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("⚠️ Iltimos, raqamda kiriting (Masalan: 1000):")
        return

    price = int(text)
    await db.set_setting("referral_price", price)
    await state.clear()
    await message.answer(
        f"✅ Referal narxi muvaffaqiyatli o'zgartirildi: <b>{price:,} UZS</b>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )

# --- VAZIFA NARXI ---
@router.message(F.text == "💵 Vazifa narxi")
async def start_set_task_price(message: Message, state: FSMContext):
    current = await db.get_setting("task_price") or 500
    await state.set_state(SetTaskPriceState.waiting_for_price)
    await message.answer(
        f"💵 <b>Standart vazifa narxini sozlash</b>\n\n"
        f"Hozirgi standart narx: <b>{current:,} UZS</b>\n\n"
        f"Yangi standart narxni kiriting:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetTaskPriceState.waiting_for_price, F.text == "❌ Bekor qilish")
async def cancel_set_task_price(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetTaskPriceState.waiting_for_price)
async def process_set_task_price(message: Message, state: FSMContext):
    text = message.text.replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("⚠️ Iltimos, raqamda kiriting (Masalan: 500):")
        return

    price = int(text)
    await db.set_setting("task_price", price)
    await state.clear()
    await message.answer(
        f"✅ Standart vazifa narxi muvaffaqiyatli o'zgartirildi: <b>{price:,} UZS</b>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )

# --- KARTA MA'LUMOTLARI ---
@router.message(F.text == "💳 Karta ma'lumotlari")
async def start_set_card(message: Message, state: FSMContext):
    cur_card = await db.get_setting("card_number") or "Kiritilmagan"
    cur_holder = await db.get_setting("card_holder") or "Kiritilmagan"
    await state.set_state(SetCardState.waiting_for_card_number)
    await message.answer(
        f"💳 <b>To'lov kartasi ma'lumotlari</b>\n\n"
        f"Hozirgi karta: <code>{cur_card}</code>\n"
        f"Karta egasi: <b>{cur_holder}</b>\n\n"
        f"1️⃣ Yangi karta raqamini kiriting:\n<i>(Masalan: 8600 1234 5678 9012)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetCardState.waiting_for_card_number, F.text == "❌ Bekor qilish")
async def cancel_set_card(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetCardState.waiting_for_card_number)
async def process_set_card_number(message: Message, state: FSMContext):
    card_number = message.text.strip()
    await state.update_data(card_number=card_number)
    await state.set_state(SetCardState.waiting_for_card_holder)
    await message.answer(
        "2️⃣ Karta egasining ism-familiyasini kiriting:\n<i>(Masalan: FALONCHI PISTONCHIYEV)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetCardState.waiting_for_card_holder, F.text == "❌ Bekor qilish")
async def cancel_set_card_holder(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetCardState.waiting_for_card_holder)
async def process_set_card_holder(message: Message, state: FSMContext):
    holder = message.text.strip()
    data = await state.get_data()
    card_number = data.get("card_number")

    await db.set_setting("card_number", card_number)
    await db.set_setting("card_holder", holder)
    await state.clear()

    await message.answer(
        f"✅ <b>Karta ma'lumotlari saqlandi!</b>\n\n"
        f"💳 Karta: <code>{card_number}</code>\n"
        f"👤 Egasi: <b>{holder}</b>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )

# --- VIDEO QO'LLANMA YUKLASH ---
@router.message(F.text == "📹 Video joylash")
async def start_set_video_guide(message: Message, state: FSMContext):
    await state.set_state(SetVideoGuideState.waiting_for_video)
    await message.answer(
        "📹 <b>Video qo'llanma yuklash</b>\n\n"
        "Foydalanuvchilar 15 000 UZS to'lab oladigan video qo'llanmani yuboring:\n"
        "<i>(Videoni izoh (caption) bilan birga yuborishingiz mumkin)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetVideoGuideState.waiting_for_video, F.text == "❌ Bekor qilish")
async def cancel_set_video(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetVideoGuideState.waiting_for_video, F.video)
async def process_video_guide(message: Message, state: FSMContext):
    video_id = message.video.file_id
    caption = message.caption or "📹 Maxsus video qo'llanma!"

    await db.set_setting("video_guide", {
        "file_id": video_id,
        "caption": caption
    })

    await state.clear()
    await message.answer(
        "✅ <b>Video qo'llanma muvaffaqiyatli saqlandi!</b>\n\n"
        "Endi foydalanuvchilar hisobida 15 000 UZS bo'lsa uni yuklab olishlari mumkin.",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetVideoGuideState.waiting_for_video)
async def invalid_video(message: Message):
    await message.answer("⚠️ Iltimos, video fayl yuboring!")

# --- REKLAMA JOYLASHTIRISH ---
@router.message(F.text == "📢 Reklama joylash")
async def start_set_ad(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(SetAdPostState.waiting_for_content)
    await message.answer(
        "📢 <b>Reklama joylashtirish bo'limi</b>\n\n"
        "Reklama postingizni (matn, rasm yoki video) yuboring:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetAdPostState.waiting_for_content, F.text == "❌ Bekor qilish")
async def cancel_ad_content(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetAdPostState.waiting_for_content)
async def process_ad_content(message: Message, state: FSMContext):
    file_type = None
    file_id = None
    caption = message.html_text if message.text else message.caption

    if message.photo:
        file_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        file_type = "video"
        file_id = message.video.file_id

    await state.update_data(
        file_type=file_type,
        file_id=file_id,
        text=caption
    )

    await state.set_state(SetAdPostState.waiting_for_button_choice)
    await message.answer(
        "🔘 Reklamaga <b>tugma</b> qo'shilsinmi?",
        reply_markup=yes_no_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetAdPostState.waiting_for_button_choice, F.text == "❌ Bekor qilish")
async def cancel_ad_btn_choice(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetAdPostState.waiting_for_button_choice)
async def process_ad_btn_choice(message: Message, state: FSMContext):
    choice = message.text.lower()
    if "ha" in choice:
        await state.update_data(has_button=True)
        await state.set_state(SetAdPostState.waiting_for_button_text)
        await message.answer(
            "Tugma matnini kiriting:\n<i>(Masalan: Batafsil ma'lumot)</i>",
            reply_markup=cancel_keyboard(),
            parse_mode="HTML"
        )
    else:
        data = await state.get_data()
        await db.set_setting("ad_post", {
            "text": data.get("text"),
            "file_id": data.get("file_id"),
            "file_type": data.get("file_type"),
            "has_button": False,
            "button_text": None,
            "button_url": None
        })
        await state.clear()
        await message.answer("✅ Reklama muvaffaqiyatli saqlandi!", reply_markup=admin_main_keyboard())

@router.message(SetAdPostState.waiting_for_button_text, F.text == "❌ Bekor qilish")
async def cancel_ad_btn_text(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetAdPostState.waiting_for_button_text)
async def process_ad_btn_text(message: Message, state: FSMContext):
    btn_text = message.text.strip()
    await state.update_data(button_text=btn_text)
    await state.set_state(SetAdPostState.waiting_for_button_url)
    await message.answer(
        "Tugma havolasini (URL) kiriting:\n<i>(Masalan: https://t.me/kanal_nomi)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetAdPostState.waiting_for_button_url, F.text == "❌ Bekor qilish")
async def cancel_ad_btn_url(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetAdPostState.waiting_for_button_url)
async def process_ad_btn_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("t.me")):
        await message.answer("⚠️ Iltimos, haqiqiy URL manzil kiriting:")
        return

    data = await state.get_data()
    await db.set_setting("ad_post", {
        "text": data.get("text"),
        "file_id": data.get("file_id"),
        "file_type": data.get("file_type"),
        "has_button": True,
        "button_text": data.get("button_text"),
        "button_url": url
    })

    await state.clear()
    await message.answer(
        "✅ <b>Tugmali reklama muvaffaqiyatli saqlandi!</b>",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML"
    )

# --- BOT HAQIDA MATNI ---
@router.message(F.text == "ℹ️ Bot haqida matni")
async def start_set_about(message: Message, state: FSMContext):
    await state.set_state(SetAboutTextState.waiting_for_text)
    await message.answer(
        "ℹ️ <b>'Bot haqida' bo'limi uchun yangi matn kiriting:</b>\n"
        "<i>(HTML teglardan foydalanishingiz mumkin: &lt;b&gt;, &lt;i&gt;, &lt;code&gt;)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetAboutTextState.waiting_for_text, F.text == "❌ Bekor qilish")
async def cancel_set_about(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetAboutTextState.waiting_for_text)
async def process_set_about(message: Message, state: FSMContext):
    text = message.html_text
    await db.set_setting("about_text", text)
    await state.clear()
    await message.answer("✅ 'Bot haqida' matni muvaffaqiyatli yangilandi!", reply_markup=admin_main_keyboard())

# --- YORDAM MATNI ---
@router.message(F.text == "🆘 Yordam matni")
async def start_set_help(message: Message, state: FSMContext):
    await state.set_state(SetHelpTextState.waiting_for_text)
    await message.answer(
        "🆘 <b>'Yordam' bo'limi uchun yangi murojaat matnini kiriting:</b>\n"
        "<i>(Masalan: Savollar bo'lsa @admin ga yozing)</i>",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )

@router.message(SetHelpTextState.waiting_for_text, F.text == "❌ Bekor qilish")
async def cancel_set_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard())

@router.message(SetHelpTextState.waiting_for_text)
async def process_set_help(message: Message, state: FSMContext):
    text = message.html_text
    await db.set_setting("help_text", text)
    await state.clear()
    await message.answer("✅ 'Yordam' matni muvaffaqiyatli yangilandi!", reply_markup=admin_main_keyboard())
