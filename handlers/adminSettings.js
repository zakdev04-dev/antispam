const { getSetting, setSetting } = require("../database");
const { adminMainKeyboard, cancelKeyboard, yesNoKeyboard } = require("../keyboards/keyboards");
const { getState, setState, clearState, updateData } = require("../state");

// 1. Referal narxi
async function handleStartSetRefPrice(ctx) {
  const current = (await getSetting("referral_price")) || 1000;
  setState(ctx.from.id, "SET_REF_PRICE");
  await ctx.replyWithHTML(
    `💰 <b>Referal narxini sozlash</b>\n\n` +
    `Hozirgi narx: <b>${current.toLocaleString()} UZS</b>\n\n` +
    `Yangi narxni so'mda (raqam bilan) kiriting:`,
    cancelKeyboard()
  );
}

// 2. Vazifa narxi
async function handleStartSetTaskPrice(ctx) {
  const current = (await getSetting("task_price")) || 500;
  setState(ctx.from.id, "SET_TASK_PRICE");
  await ctx.replyWithHTML(
    `💵 <b>Standart vazifa narxini sozlash</b>\n\n` +
    `Hozirgi standart narx: <b>${current.toLocaleString()} UZS</b>\n\n` +
    `Yangi standart narxni kiriting:`,
    cancelKeyboard()
  );
}

// 3. Karta ma'lumotlari
async function handleStartSetCard(ctx) {
  const curCard = (await getSetting("card_number")) || "Kiritilmagan";
  const curHolder = (await getSetting("card_holder")) || "Kiritilmagan";
  setState(ctx.from.id, "SET_CARD_NUMBER");
  await ctx.replyWithHTML(
    `💳 <b>To'lov kartasi ma'lumotlari</b>\n\n` +
    `Hozirgi karta: <code>${curCard}</code>\n` +
    `Karta egasi: <b>${curHolder}</b>\n\n` +
    `1️⃣ Yangi karta raqamini kiriting:\n<i>(Masalan: 8600 1234 5678 9012)</i>`,
    cancelKeyboard()
  );
}

// 4. Video joylash
async function handleStartSetVideoGuide(ctx) {
  setState(ctx.from.id, "SET_VIDEO_GUIDE");
  await ctx.replyWithHTML(
    `📹 <b>Video qo'llanma yuklash</b>\n\n` +
    `Foydalanuvchilar 15 000 UZS to'lab oladigan video qo'llanmani yuboring:\n` +
    `<i>(Videoni izoh (caption) bilan birga yuborishingiz mumkin)</i>`,
    cancelKeyboard()
  );
}

// 5. Reklama joylash
async function handleStartSetAd(ctx) {
  clearState(ctx.from.id);
  setState(ctx.from.id, "SET_AD_CONTENT");
  await ctx.replyWithHTML(
    `📢 <b>Reklama joylashtirish bo'limi</b>\n\n` +
    `Reklama postingizni (matn, rasm yoki video) yuboring:`,
    cancelKeyboard()
  );
}

// 6. Bot haqida matni
async function handleStartSetAbout(ctx) {
  setState(ctx.from.id, "SET_ABOUT_TEXT");
  await ctx.replyWithHTML(
    `ℹ️ <b>'Bot haqida' bo'limi uchun yangi matn kiriting:</b>\n` +
    `<i>(HTML teglardan foydalanishingiz mumkin)</i>`,
    cancelKeyboard()
  );
}

// 7. Yordam matni
async function handleStartSetHelp(ctx) {
  setState(ctx.from.id, "SET_HELP_TEXT");
  await ctx.replyWithHTML(
    `🆘 <b>'Yordam' bo'limi uchun yangi murojaat matnini kiriting:</b>\n` +
    `<i>(Masalan: Savollar bo'lsa @admin ga yozing)</i>`,
    cancelKeyboard()
  );
}

async function handleAdminSettingsInput(ctx) {
  const userId = ctx.from.id;
  const userState = getState(userId);
  if (!userState) return false;

  const text = (ctx.message.text || "").trim();
  if (text === "❌ Bekor qilish") {
    clearState(userId);
    await ctx.reply("Amal bekor qilindi.", adminMainKeyboard());
    return true;
  }

  // Referal narxi
  if (userState.state === "SET_REF_PRICE") {
    const cleanNum = text.replace(/\s+/g, "").replace(/,/g, "");
    if (!/^\d+$/.test(cleanNum)) {
      await ctx.reply("⚠️ Iltimos, raqamda kiriting (Masalan: 1000):");
      return true;
    }
    const price = parseInt(cleanNum, 10);
    await setSetting("referral_price", price);
    clearState(userId);
    await ctx.replyWithHTML(`✅ Referal narxi o'zgartirildi: <b>${price.toLocaleString()} UZS</b>`, adminMainKeyboard());
    return true;
  }

  // Vazifa narxi
  if (userState.state === "SET_TASK_PRICE") {
    const cleanNum = text.replace(/\s+/g, "").replace(/,/g, "");
    if (!/^\d+$/.test(cleanNum)) {
      await ctx.reply("⚠️ Iltimos, raqamda kiriting (Masalan: 500):");
      return true;
    }
    const price = parseInt(cleanNum, 10);
    await setSetting("task_price", price);
    clearState(userId);
    await ctx.replyWithHTML(`✅ Standart vazifa narxi o'zgartirildi: <b>${price.toLocaleString()} UZS</b>`, adminMainKeyboard());
    return true;
  }

  // Karta raqami
  if (userState.state === "SET_CARD_NUMBER") {
    updateData(userId, { cardNumber: text });
    setState(userId, "SET_CARD_HOLDER", userState.data);
    updateData(userId, { cardNumber: text });
    await ctx.replyWithHTML(
      "2️⃣ Karta egasining ism-familiyasini kiriting:\n<i>(Masalan: FALONCHI PISTONCHIYEV)</i>",
      cancelKeyboard()
    );
    return true;
  }

  // Karta egasi
  if (userState.state === "SET_CARD_HOLDER") {
    const { cardNumber } = userState.data;
    await setSetting("card_number", cardNumber);
    await setSetting("card_holder", text);
    clearState(userId);
    await ctx.replyWithHTML(
      `✅ <b>Karta ma'lumotlari saqlandi!</b>\n\n` +
      `💳 Karta: <code>${cardNumber}</code>\n` +
      `👤 Egasi: <b>${text}</b>`,
      adminMainKeyboard()
    );
    return true;
  }

  // Video qo'llanma yuklash
  if (userState.state === "SET_VIDEO_GUIDE") {
    if (!ctx.message.video) {
      await ctx.reply("⚠️ Iltimos, video fayl yuboring!");
      return true;
    }
    const videoId = ctx.message.video.file_id;
    const caption = ctx.message.caption || "📹 Maxsus video qo'llanma!";
    await setSetting("video_guide", { file_id: videoId, caption });
    clearState(userId);
    await ctx.replyWithHTML(
      "✅ <b>Video qo'llanma muvaffaqiyatli saqlandi!</b>\n\n" +
      "Endi foydalanuvchilar hisobida 15 000 UZS bo'lsa uni yuklab olishlari mumkin.",
      adminMainKeyboard()
    );
    return true;
  }

  // Reklama: kontent
  if (userState.state === "SET_AD_CONTENT") {
    let fileType = null;
    let fileId = null;
    let caption = ctx.message.caption || ctx.message.text || "";

    if (ctx.message.photo && ctx.message.photo.length > 0) {
      fileType = "photo";
      fileId = ctx.message.photo[ctx.message.photo.length - 1].file_id;
    } else if (ctx.message.video) {
      fileType = "video";
      fileId = ctx.message.video.file_id;
    }

    setState(userId, "SET_AD_BTN_CHOICE", { fileType, fileId, text: caption });
    await ctx.replyWithHTML("🔘 Reklamaga <b>tugma</b> qo'shilsinmi?", yesNoKeyboard());
    return true;
  }

  // Reklama: tugma tanlovi
  if (userState.state === "SET_AD_BTN_CHOICE") {
    const choice = text.toLowerCase();
    if (choice.includes("ha")) {
      updateData(userId, { hasButton: true });
      setState(userId, "SET_AD_BTN_TEXT", userState.data);
      updateData(userId, { hasButton: true });
      await ctx.replyWithHTML("Tugma matnini kiriting:\n<i>(Masalan: Batafsil ma'lumot)</i>", cancelKeyboard());
    } else {
      const { text: adText, fileId, fileType } = userState.data;
      await setSetting("ad_post", {
        text: adText,
        file_id: fileId,
        file_type: fileType,
        has_button: false,
        button_text: null,
        button_url: null
      });
      clearState(userId);
      await ctx.reply("✅ Reklama muvaffaqiyatli saqlandi!", adminMainKeyboard());
    }
    return true;
  }

  // Reklama: tugma matni
  if (userState.state === "SET_AD_BTN_TEXT") {
    updateData(userId, { buttonText: text });
    setState(userId, "SET_AD_BTN_URL", userState.data);
    updateData(userId, { buttonText: text });
    await ctx.replyWithHTML("Tugma havolasini (URL) kiriting:\n<i>(Masalan: https://t.me/kanal_nomi)</i>", cancelKeyboard());
    return true;
  }

  // Reklama: tugma URL
  if (userState.state === "SET_AD_BTN_URL") {
    if (!text.startsWith("http://") && !text.startsWith("https://") && !text.startsWith("t.me")) {
      await ctx.reply("⚠️ Iltimos, haqiqiy URL manzil kiriting:");
      return true;
    }

    const { text: adText, fileId, fileType, buttonText } = userState.data;
    await setSetting("ad_post", {
      text: adText,
      file_id: fileId,
      file_type: fileType,
      has_button: true,
      button_text: buttonText,
      button_url: text
    });
    clearState(userId);
    await ctx.replyWithHTML("✅ <b>Tugmali reklama muvaffaqiyatli saqlandi!</b>", adminMainKeyboard());
    return true;
  }

  // Bot haqida matni
  if (userState.state === "SET_ABOUT_TEXT") {
    await setSetting("about_text", text);
    clearState(userId);
    await ctx.reply("✅ 'Bot haqida' matni muvaffaqiyatli yangilandi!", adminMainKeyboard());
    return true;
  }

  // Yordam matni
  if (userState.state === "SET_HELP_TEXT") {
    await setSetting("help_text", text);
    clearState(userId);
    await ctx.reply("✅ 'Yordam' matni muvaffaqiyatli yangilandi!", adminMainKeyboard());
    return true;
  }

  return false;
}

module.exports = {
  handleStartSetRefPrice,
  handleStartSetTaskPrice,
  handleStartSetCard,
  handleStartSetVideoGuide,
  handleStartSetAd,
  handleStartSetAbout,
  handleStartSetHelp,
  handleAdminSettingsInput
};
