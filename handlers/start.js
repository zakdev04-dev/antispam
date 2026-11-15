const { User, getOrCreateUser, getSetting } = require("../database");
const { contactKeyboard, mainMenuKeyboard, mandatoryChannelsKeyboard } = require("../keyboards/keyboards");
const { getUnsubscribedChannels } = require("../services/checker");
const { clearState } = require("../state");

async function handleStart(ctx) {
  const userId = ctx.from.id;
  clearState(userId);

  const startPayload = ctx.startPayload || "";
  let referrerId = null;
  if (startPayload.startsWith("ref_")) {
    const rawRef = startPayload.replace("ref_", "");
    if (/^\d+$/.test(rawRef) && parseInt(rawRef, 10) !== userId) {
      referrerId = parseInt(rawRef, 10);
    }
  }

  const user = await getOrCreateUser(
    userId,
    ctx.from.first_name,
    ctx.from.last_name,
    ctx.from.username,
    referrerId
  );

  if (!user.phone) {
    const welcome = (
      `Assalomu alaykum, <b>${ctx.from.first_name || "Foydalanuvchi"}</b>!\n\n` +
      `Botimizga xush kelibsiz! Bot imkoniyatlaridan to'liq foydalanish uchun ` +
      `iltimos, pastdagi tugma orqali telefon raqamingizni ulashing.`
    );
    return ctx.replyWithHTML(welcome, contactKeyboard());
  }

  await showChannelsOrMainMenu(ctx, userId);
}

async function handleContact(ctx) {
  const userId = ctx.from.id;
  if (!ctx.message || !ctx.message.contact) return;

  let phone = ctx.message.contact.phone_number;
  if (!phone.startsWith("+")) phone = "+" + phone;

  await User.updateOne({ userId }, { phone });
  await ctx.reply("✅ Telefon raqamingiz muvaffaqiyatli qabul qilindi!");

  // Baza kanalga bildirishnoma yuborish
  await sendNewUserNotificationToDatabaseChannel(ctx.telegram, userId, phone);

  await showChannelsOrMainMenu(ctx, userId);
}

async function sendNewUserNotificationToDatabaseChannel(telegram, userId, phone) {
  try {
    const user = await User.findOne({ userId });
    if (!user || user.notifiedDatabaseChannel) return;

    const dbChannel = await getSetting("database_channel");
    if (!dbChannel) return;

    const name = `${user.firstName || ""} ${user.lastName || ""}`.trim() || "Noma'lum";
    const username = user.username ? `@${user.username}` : "Mavjud emas";
    const regDate = user.createdAt
      ? new Date(user.createdAt).toLocaleString("uz-UZ", { timeZone: "Asia/Tashkent" })
      : new Date().toLocaleString("uz-UZ");

    const notificationText = (
      `👤 <b>Yangi foydalanuvchi qo'shildi!</b>\n\n` +
      `🏷 <b>Ismi:</b> ${name}\n` +
      `🌐 <b>Username:</b> ${username}\n` +
      `🆔 <b>Telegram ID:</b> <code>${userId}</code>\n` +
      `📱 <b>Telefon raqami:</b> <code>${phone}</code>\n` +
      `📅 <b>Qo'shilgan sana:</b> ${regDate}`
    );

    await telegram.sendMessage(dbChannel, notificationText, { parse_mode: "HTML" });
    user.notifiedDatabaseChannel = true;
    await user.save();
    console.log(`Baza kanalga yangi foydalanuvchi yuborildi: ${userId}`);
  } catch (err) {
    console.error("Baza kanalga xabar yuborishda xatolik:", err.message);
  }
}

async function showChannelsOrMainMenu(ctx, userId) {
  const unsubscribed = await getUnsubscribedChannels(ctx.telegram, userId);

  if (unsubscribed && unsubscribed.length > 0) {
    const text = (
      "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n" +
      "<i>(Obuna bo'lgan kanallaringiz ro'yxatdan avtomatik olib tashlanadi)</i>"
    );
    const kb = mandatoryChannelsKeyboard(unsubscribed);
    if (ctx.callbackQuery) {
      try {
        await ctx.editMessageText(text, { parse_mode: "HTML", ...kb });
      } catch (e) {
        await ctx.replyWithHTML(text, kb);
      }
    } else {
      await ctx.replyWithHTML(text, kb);
    }
  } else {
    await rewardReferrerIfNeeded(ctx.telegram, userId);
    const text = (
      "🎉 <b>Xush kelibsiz!</b>\n\n" +
      "Siz barcha majburiy kanallarga a'zo bo'ldingiz.\n" +
      "Quyidagi menyu orqali botdan foydalanishingiz mumkin:"
    );
    if (ctx.callbackQuery) {
      try {
        await ctx.deleteMessage();
      } catch (e) {}
      await ctx.telegram.sendMessage(userId, text, {
        parse_mode: "HTML",
        ...mainMenuKeyboard()
      });
    } else {
      await ctx.replyWithHTML(text, mainMenuKeyboard());
    }
  }
}

async function rewardReferrerIfNeeded(telegram, userId) {
  const user = await User.findOne({ userId });
  if (user && user.referrerId && !user.referralRewarded) {
    const referrerId = user.referrerId;
    const refPrice = (await getSetting("referral_price")) || 1000;

    await User.updateOne({ userId: referrerId }, { $inc: { balance: refPrice } });
    user.referralRewarded = true;
    await user.save();

    try {
      await telegram.sendMessage(
        referrerId,
        `🎉 <b>Yangi do'st taklif qilindi!</b>\n\n` +
        `Sizning taklif havolangiz orqali kirgan do'stingiz barcha shartlarni bajardi. ` +
        `Balansingizga <b>+${refPrice.toLocaleString()} UZS</b> qo'shildi!`,
        { parse_mode: "HTML" }
      );
    } catch (e) {}
  }
}

async function handleCheckSubscription(ctx) {
  const userId = ctx.from.id;
  const unsubscribed = await getUnsubscribedChannels(ctx.telegram, userId);

  if (unsubscribed && unsubscribed.length > 0) {
    await ctx.answerCbQuery("❌ Siz hali barcha kanallarga obuna bo'lmadingiz!", { show_alert: true });
    const text = (
      "⚠️ <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n" +
      "<i>(Obuna bo'lgan kanallaringiz ro'yxatdan avtomatik olib tashlanadi)</i>"
    );
    const kb = mandatoryChannelsKeyboard(unsubscribed);
    try {
      await ctx.editMessageText(text, { parse_mode: "HTML", ...kb });
    } catch (e) {}
  } else {
    await ctx.answerCbQuery("✅ Tabriklaymiz, barcha kanallarga a'zo bo'ldingiz!");
    await showChannelsOrMainMenu(ctx, userId);
  }
}

module.exports = {
  handleStart,
  handleContact,
  handleCheckSubscription,
  showChannelsOrMainMenu
};
