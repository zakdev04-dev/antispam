const { Payment, User, getSetting } = require("../database");
const config = require("../config");
const { getState, setState, clearState } = require("../state");
const { cancelKeyboard, mainMenuKeyboard, paymentConfirmKeyboard } = require("../keyboards/keyboards");

async function handleTopUpCallback(ctx) {
  const userId = ctx.from.id;
  await ctx.answerCbQuery();
  setState(userId, "WAITING_FOR_AMOUNT");

  await ctx.replyWithHTML(
    "💳 <b>Hisobni to'ldirish</b>\n\n" +
    "Qancha summaga hisobingizni to'ldirmoqchisiz?\n" +
    "Iltimos, summani so'mda (raqamlar bilan) kiriting:\n" +
    "<i>(Masalan: 15000 yoki 50000)</i>",
    cancelKeyboard()
  );
}

async function handlePaymentText(ctx) {
  const userId = ctx.from.id;
  const userState = getState(userId);
  if (!userState) return false;

  const text = (ctx.message.text || "").trim();

  if (text === "❌ Bekor qilish") {
    clearState(userId);
    await ctx.reply("To'lov bekor qilindi.", mainMenuKeyboard());
    return true;
  }

  if (userState.state === "WAITING_FOR_AMOUNT") {
    const cleanNum = text.replace(/\s+/g, "").replace(/,/g, "");
    const amount = parseInt(cleanNum, 10);

    if (isNaN(amount) || amount < 1000) {
      await ctx.reply("⚠️ Iltimos, to'g'ri summa kiriting (kamida 1,000 UZS)!\nMasalan: 20000");
      return true;
    }

    const cardNumber = (await getSetting("card_number")) || "8600 0000 0000 0000";
    const cardHolder = (await getSetting("card_holder")) || "ADMIN";
    const name = ctx.from.first_name || "Foydalanuvchi";

    setState(userId, "WAITING_FOR_RECEIPT", { amount });

    const info = (
      `Hurmatli <b>${name}</b>, siz admin kiritgan karta:\n` +
      `💳 <code>${cardNumber}</code>\n` +
      `👤 Egasi: <b>${cardHolder}</b>\n\n` +
      `Kiritilgan summa: <b>${amount.toLocaleString()} UZS</b>.\n\n` +
      `To'lovni amalga oshiring va <b>to'lov chekini</b> (skrinshot yoki rasm) shu yerga yuboring:`
    );

    await ctx.replyWithHTML(info, cancelKeyboard());
    return true;
  }

  return false;
}

async function handleReceipt(ctx) {
  const userId = ctx.from.id;
  const userState = getState(userId);
  if (!userState || userState.state !== "WAITING_FOR_RECEIPT") return false;

  let fileId = null;
  let fileType = "photo";

  if (ctx.message.photo && ctx.message.photo.length > 0) {
    fileId = ctx.message.photo[ctx.message.photo.length - 1].file_id;
    fileType = "photo";
  } else if (ctx.message.document) {
    fileId = ctx.message.document.file_id;
    fileType = "document";
  }

  if (!fileId) {
    await ctx.reply("⚠️ Iltimos, to'lov chekini rasm yoki hujjat ko'rinishida yuboring!");
    return true;
  }

  const amount = userState.data.amount || 0;
  clearState(userId);

  const payment = await Payment.create({
    userId,
    amount,
    fileId,
    fileType,
    status: "pending"
  });

  await ctx.replyWithHTML(
    "✅ <b>To'lov cheki qabul qilindi!</b>\n\n" +
    "Adminlarimiz chekni tekshirgandan so'ng hisobingizga mablag' qo'shiladi " +
    "va sizga xabar beriladi. Iltimos, kuting!",
    mainMenuKeyboard()
  );

  const name = `${ctx.from.first_name || ""} ${ctx.from.last_name || ""}`.trim() || "Foydalanuvchi";
  const username = ctx.from.username ? `@${ctx.from.username}` : "yo'q";

  const adminCaption = (
    `💰 <b>Yangi to'lov so'rovi!</b>\n\n` +
    `🆔 To'lov ID: <code>${payment._id}</code>\n` +
    `👤 Foydalanuvchi: <b>${name}</b> (${username})\n` +
    `🆔 Telegram ID: <code>${userId}</code>\n` +
    `💵 Summa: <b>${amount.toLocaleString()} UZS</b>\n\n` +
    `Iltimos, chekni tekshirib qaror qabul qiling:`
  );

  for (const adminId of config.ADMINS) {
    try {
      if (fileType === "photo") {
        await ctx.telegram.sendPhoto(adminId, fileId, {
          caption: adminCaption,
          parse_mode: "HTML",
          ...paymentConfirmKeyboard(payment._id)
        });
      } else {
        await ctx.telegram.sendDocument(adminId, fileId, {
          caption: adminCaption,
          parse_mode: "HTML",
          ...paymentConfirmKeyboard(payment._id)
        });
      }
    } catch (e) {
      console.warn(`Adminga to'lov yuborishda xatolik (${adminId}):`, e.message);
    }
  }

  return true;
}

async function handleApprovePayment(ctx) {
  const paymentId = ctx.match[1];
  const payment = await Payment.findById(paymentId);

  if (!payment) {
    return ctx.answerCbQuery("To'lov topilmadi!", { show_alert: true });
  }

  if (payment.status !== "pending") {
    return ctx.answerCbQuery("Bu to'lovga allaqachon javob berilgan!", { show_alert: true });
  }

  payment.status = "approved";
  await payment.save();

  await User.updateOne({ userId: payment.userId }, { $inc: { balance: payment.amount } });
  const user = await User.findOne({ userId: payment.userId });
  const newBalance = user ? user.balance : payment.amount;

  try {
    await ctx.telegram.sendMessage(
      payment.userId,
      `✅ <b>To'lovingiz tasdiqlandi!</b>\n\n` +
      `Hisobingizga <b>+${payment.amount.toLocaleString()} UZS</b> qo'shildi.\n` +
      `Joriy balansingiz: <b>${newBalance.toLocaleString()} UZS</b>.\n\n` +
      `<i>Botdan unumli foydalanishingizni tilaymiz!</i>`,
      { parse_mode: "HTML" }
    );
  } catch (e) {}

  try {
    await ctx.editMessageCaption(
      `${ctx.callbackQuery.message.caption || ""}\n\n` +
      `✅ <b>TASDIQLANDI!</b> (+${payment.amount.toLocaleString()} UZS)\n` +
      `Admin: ${ctx.from.first_name || "Admin"}`,
      { parse_mode: "HTML" }
    );
  } catch (e) {}

  await ctx.answerCbQuery("To'lov tasdiqlandi!");
}

async function handleRejectPayment(ctx) {
  const paymentId = ctx.match[1];
  const payment = await Payment.findById(paymentId);

  if (!payment) {
    return ctx.answerCbQuery("To'lov topilmadi!", { show_alert: true });
  }

  if (payment.status !== "pending") {
    return ctx.answerCbQuery("Bu to'lovga allaqachon javob berilgan!", { show_alert: true });
  }

  payment.status = "rejected";
  await payment.save();

  try {
    await ctx.telegram.sendMessage(
      payment.userId,
      `❌ <b>To'lovingiz bekor qilindi!</b>\n\n` +
      `Kiritilgan summa: ${payment.amount.toLocaleString()} UZS.\n` +
      `Agar to'lov qilgan bo'lsangiz adminga murojaat qiling.`,
      { parse_mode: "HTML" }
    );
  } catch (e) {}

  try {
    await ctx.editMessageCaption(
      `${ctx.callbackQuery.message.caption || ""}\n\n` +
      `❌ <b>BEKOR QILINDI!</b>\n` +
      `Admin: ${ctx.from.first_name || "Admin"}`,
      { parse_mode: "HTML" }
    );
  } catch (e) {}

  await ctx.answerCbQuery("To'lov bekor qilindi!");
}

module.exports = {
  handleTopUpCallback,
  handlePaymentText,
  handleReceipt,
  handleApprovePayment,
  handleRejectPayment
};
