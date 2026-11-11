const { User, getSetting } = require("../database");
const config = require("../config");
const {
  cabinetKeyboard,
  quickFillBalanceKeyboard,
  shareReferralKeyboard,
  customAdKeyboard
} = require("../keyboards/keyboards");

async function handleVideoGuide(ctx) {
  const userId = ctx.from.id;
  const user = await User.findOne({ userId });
  const balance = user ? user.balance : 0;
  const price = config.VIDEO_PRICE;

  const guide = await getSetting("video_guide");
  if (!guide || !guide.file_id) {
    return ctx.replyWithHTML(
      "📹 <b>Video qo'llanma tez orada yuklanadi!</b>\n\nAdmin hozirda yangi material tayyorlamoqda."
    );
  }

  if (balance < price) {
    return ctx.replyWithHTML(
      `❌ <b>Hisobingizda mablag' yetarli emas!</b>\n\n` +
      `📹 Video qo'llanma narxi: <b>${price.toLocaleString()} UZS</b>\n` +
      `💳 Sizning balansingiz: <b>${balance.toLocaleString()} UZS</b>\n\n` +
      `Qo'llanmani olish uchun hisobingizni to'ldiring:`,
      quickFillBalanceKeyboard()
    );
  }

  // Balansdan yechib olish
  await User.updateOne({ userId }, { $inc: { balance: -price }, hasVideoAccess: true });

  await ctx.replyWithHTML(
    `✅ Hisobingizdan <b>${price.toLocaleString()} UZS</b> yechildi!\nSizga video qo'llanma yuborilmoqda...`
  );

  try {
    await ctx.replyWithVideo(guide.file_id, {
      caption: `${guide.caption || "📹 Mana siz kutgan video qo'llanma!"}\n\n<i>Qo'llanmani yaxshilab o'rganib chiqing!</i>`,
      parse_mode: "HTML"
    });
  } catch (err) {
    console.error("Video yuborishda xatolik:", err);
    ctx.reply("⚠️ Video yuborishda xatolik yuz berdi. Iltimos adminga murojaat qiling.");
  }
}

async function handleCabinet(ctx) {
  const userId = ctx.from.id;
  const user = await User.findOne({ userId });
  if (!user) {
    return ctx.reply("Iltimos, qayta /start buyrug'ini yuboring.");
  }

  const name = `${user.firstName || ""} ${user.lastName || ""}`.trim() || "Foydalanuvchi";
  const username = user.username ? `@${user.username}` : "Mavjud emas";
  const phone = user.phone || "Kiritilmagan";
  const balance = (user.balance || 0).toLocaleString();

  const regDate = user.createdAt ? new Date(user.createdAt).toLocaleString("uz-UZ") : "Noma'lum";

  const text = (
    `👤 <b>Sizning shaxsiy kabinetingiz:</b>\n\n` +
    `🏷 <b>Ism:</b> ${name}\n` +
    `🌐 <b>Username:</b> ${username}\n` +
    `🆔 <b>Telegram ID:</b> <code>${userId}</code>\n` +
    `📱 <b>Telefon raqam:</b> ${phone}\n` +
    `💰 <b>Hisobingiz:</b> <b>${balance} UZS</b>\n` +
    `📅 <b>Qo'shilgan sana:</b> ${regDate}\n\n` +
    `<i>Hisobingizni to'ldirishingiz yoki vazifalarni bajarib pul ishlashingiz mumkin!</i>`
  );

  await ctx.replyWithHTML(text, cabinetKeyboard());
}

async function handleReferral(ctx) {
  const userId = ctx.from.id;
  const botInfo = await ctx.telegram.getMe();
  const refLink = `https://t.me/${botInfo.username}?start=ref_${userId}`;
  const refPrice = (await getSetting("referral_price")) || 1000;

  const creativePost = (
    `🚀 <b>Do'stlaringizni taklif qiling va pul ishlang!</b>\n\n` +
    `Har bir taklif qilgan faol do'stingiz uchun sizga <b>${refPrice.toLocaleString()} UZS</b> beriladi! 💸\n\n` +
    `Sizning shaxsiy taklif havolangiz:\n` +
    `👉 <code>${refLink}</code>\n\n` +
    `🎯 <b>Qanday ishlaydi?</b>\n` +
    `1. Ushbu havolani do'stlaringizga, guruhlarga yoki kanallarga tarqating.\n` +
    `2. Do'stingiz botga kirib, ro'yxatdan o'tadi.\n` +
    `3. U bot shartlarini bajargan zahoti balansingizga pul tushadi!\n\n` +
    `<i>Hoziroq 'Ulashish' tugmasini bosing va do'stlaringizni taklif qilishni boshlang! 👇</i>`
  );

  await ctx.replyWithHTML(creativePost, shareReferralKeyboard(botInfo.username, userId));
}

async function handleAdSection(ctx) {
  const ad = await getSetting("ad_post");
  if (!ad) {
    return ctx.reply("📢 Hozircha faol reklama mavjud emas.");
  }

  const text = ad.text || "📢 Bu yerda sizning reklamangiz bo'lishi mumkin!";
  const fileId = ad.file_id;
  const fileType = ad.file_type;
  const hasButton = ad.has_button;

  let extra = { parse_mode: "HTML" };
  if (hasButton && ad.button_text && ad.button_url) {
    extra = { ...extra, ...customAdKeyboard(ad.button_text, ad.button_url) };
  }

  if (fileId && fileType === "photo") {
    await ctx.replyWithPhoto(fileId, { caption: text, ...extra });
  } else if (fileId && fileType === "video") {
    await ctx.replyWithVideo(fileId, { caption: text, ...extra });
  } else {
    await ctx.replyWithHTML(text, extra);
  }
}

async function handleAbout(ctx) {
  const text = (await getSetting("about_text")) || "ℹ️ Bot haqida ma'lumot tez orada joylanadi.";
  await ctx.replyWithHTML(text);
}

async function handleHelp(ctx) {
  const text = (await getSetting("help_text")) || "🆘 Yordam: @admin bilan bog'laning.";
  await ctx.replyWithHTML(text);
}

module.exports = {
  handleVideoGuide,
  handleCabinet,
  handleReferral,
  handleAdSection,
  handleAbout,
  handleHelp
};
