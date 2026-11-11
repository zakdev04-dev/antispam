const { User } = require("../database");
const { cancelKeyboard, yesNoKeyboard, broadcastConfirmKeyboard, adminMainKeyboard, customAdKeyboard } = require("../keyboards/keyboards");
const { getState, setState, clearState, updateData } = require("../state");

async function handleStartBroadcast(ctx) {
  clearState(ctx.from.id);
  setState(ctx.from.id, "BROADCAST_MESSAGE");

  await ctx.replyWithHTML(
    "✉️ <b>Foydalanuvchilarga xabar yuborish (Rassilka)</b>\n\n" +
    "Yubormoqchi bo'lgan xabaringizni (matn, rasm yoki video) yuboring:",
    cancelKeyboard()
  );
}

async function handleBroadcastInput(ctx) {
  const userId = ctx.from.id;
  const userState = getState(userId);
  if (!userState) return false;

  const text = (ctx.message.text || "").trim();
  if (text === "❌ Bekor qilish") {
    clearState(userId);
    await ctx.reply("Xabar yuborish bekor qilindi.", adminMainKeyboard());
    return true;
  }

  // 1. Xabar qabul qilish (matn, rasm yoki video)
  if (userState.state === "BROADCAST_MESSAGE") {
    let contentType = "text";
    let fileId = null;
    let caption = ctx.message.caption || ctx.message.text || "";

    if (ctx.message.photo && ctx.message.photo.length > 0) {
      contentType = "photo";
      fileId = ctx.message.photo[ctx.message.photo.length - 1].file_id;
    } else if (ctx.message.video) {
      contentType = "video";
      fileId = ctx.message.video.file_id;
    }

    setState(userId, "BROADCAST_BTN_CHOICE", { contentType, fileId, text: caption });

    await ctx.replyWithHTML(
      "🔘 Xabarga <b>havola tugmasi (URL button)</b> qo'shilsinmi?",
      yesNoKeyboard()
    );
    return true;
  }

  // 2. Tugma tanlovi
  if (userState.state === "BROADCAST_BTN_CHOICE") {
    const choice = text.toLowerCase();
    if (choice.includes("ha")) {
      updateData(userId, { hasButton: true });
      setState(userId, "BROADCAST_BTN_TEXT", userState.data);
      updateData(userId, { hasButton: true });

      await ctx.replyWithHTML(
        "Tugma matnini kiriting:\n<i>(Masalan: Kanalga o'tish)</i>",
        cancelKeyboard()
      );
    } else {
      updateData(userId, { hasButton: false, buttonText: null, buttonUrl: null });
      await showBroadcastPreview(ctx, userId);
    }
    return true;
  }

  // 3. Tugma matni
  if (userState.state === "BROADCAST_BTN_TEXT") {
    updateData(userId, { buttonText: text });
    setState(userId, "BROADCAST_BTN_URL", userState.data);
    updateData(userId, { buttonText: text });

    await ctx.replyWithHTML(
      "Tugma havolasini (URL) kiriting:\n<i>(Masalan: https://t.me/kanal_nomi)</i>",
      cancelKeyboard()
    );
    return true;
  }

  // 4. Tugma URL
  if (userState.state === "BROADCAST_BTN_URL") {
    if (!text.startsWith("http://") && !text.startsWith("https://") && !text.startsWith("t.me")) {
      await ctx.reply("⚠️ Iltimos, haqiqiy havola (URL) kiriting:");
      return true;
    }

    updateData(userId, { buttonUrl: text });
    await showBroadcastPreview(ctx, userId);
    return true;
  }

  return false;
}

async function showBroadcastPreview(ctx, userId) {
  const userState = getState(userId);
  const { contentType, fileId, text, hasButton, buttonText, buttonUrl } = userState.data;

  let extra = { parse_mode: "HTML" };
  if (hasButton && buttonText && buttonUrl) {
    extra = { ...extra, ...customAdKeyboard(buttonText, buttonUrl) };
  }

  await ctx.replyWithHTML("👀 <b>Xabarning ko'rinishi (Preview):</b>");

  if (contentType === "photo") {
    await ctx.replyWithPhoto(fileId, { caption: text, ...extra });
  } else if (contentType === "video") {
    await ctx.replyWithVideo(fileId, { caption: text, ...extra });
  } else {
    await ctx.replyWithHTML(text || " ", extra);
  }

  setState(userId, "BROADCAST_CONFIRM", userState.data);
  await ctx.replyWithHTML("Barcha foydalanuvchilarga yuborilsinmi?", broadcastConfirmKeyboard());
}

async function handleBroadcastConfirm(ctx) {
  const userId = ctx.from.id;
  const userState = getState(userId);
  if (!userState || userState.state !== "BROADCAST_CONFIRM") {
    return ctx.answerCbQuery();
  }

  const { contentType, fileId, text, hasButton, buttonText, buttonUrl } = userState.data;
  clearState(userId);

  try {
    await ctx.editMessageText("🚀 Xabar yuborish boshlandi, iltimos kuting...");
  } catch (e) {}

  let extra = { parse_mode: "HTML" };
  if (hasButton && buttonText && buttonUrl) {
    extra = { ...extra, ...customAdKeyboard(buttonText, buttonUrl) };
  }

  const users = await User.find();
  let successCount = 0;
  let blockedCount = 0;

  for (const u of users) {
    try {
      if (contentType === "photo") {
        await ctx.telegram.sendPhoto(u.userId, fileId, { caption: text, ...extra });
      } else if (contentType === "video") {
        await ctx.telegram.sendVideo(u.userId, fileId, { caption: text, ...extra });
      } else {
        await ctx.telegram.sendMessage(u.userId, text || " ", extra);
      }
      successCount++;
      await new Promise((r) => setTimeout(r, 40));
    } catch (err) {
      blockedCount++;
      if (err.response && err.response.error_code === 403) {
        await User.updateOne({ userId: u.userId }, { isActive: false });
      }
    }
  }

  const report = (
    `✅ <b>Xabar yuborish yakunlandi!</b>\n\n` +
    `📨 Muvaffaqiyatli yetkazildi: <b>${successCount}</b> ta\n` +
    `🚫 Bloklagan yoki yetib bormagan: <b>${blockedCount}</b> ta`
  );

  await ctx.replyWithHTML(report, adminMainKeyboard());
  await ctx.answerCbQuery();
}

async function handleBroadcastCancel(ctx) {
  clearState(ctx.from.id);
  try {
    await ctx.editMessageText("Xabar yuborish bekor qilindi.");
  } catch (e) {}
  await ctx.reply("Asosiy panel:", adminMainKeyboard());
  await ctx.answerCbQuery();
}

module.exports = {
  handleStartBroadcast,
  handleBroadcastInput,
  handleBroadcastConfirm,
  handleBroadcastCancel
};
