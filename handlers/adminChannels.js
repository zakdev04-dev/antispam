const { Channel } = require("../database");
const { channelTypeInlineKb, manageChannelsKeyboard, adminMainKeyboard, cancelKeyboard } = require("../keyboards/keyboards");
const { getState, setState, clearState, updateData } = require("../state");

async function handleStartAddChannel(ctx) {
  clearState(ctx.from.id);
  await ctx.replyWithHTML(
    "📢 <b>Kanal ulash bo'limi</b>\n\n" +
    "Qaysi turdagi kanal yoki havolani ulamoqchisiz?\n" +
    "<i>Tugma nomi avtomatik tarzda <b>&lt; Obuna bo'lish &gt;</b> deb o'rnatiladi.</i>",
    channelTypeInlineKb()
  );
}

async function handleChooseChannelType(ctx) {
  const chType = ctx.match[1];
  const userId = ctx.from.id;

  setState(userId, "ADD_CH_TITLE", { chType });

  const typeDescs = {
    public: "Ochiq kanal (@username)",
    private: "Shaxsiy (Private) kanal",
    join_request: "Zayafkali kanal (Kirish so'rovi)",
    external: "Tashqi havola (Web sayt yoki boshqa havola)"
  };

  try {
    await ctx.deleteMessage();
  } catch (e) {}

  await ctx.replyWithHTML(
    `Tanlangan tur: <b>${typeDescs[chType] || chType}</b>\n\n` +
    `1️⃣ Ushbu kanal/havola uchun nom (sarlavha) kiriting:\n` +
    `<i>(Masalan: Asosiy Yangiliklar kanali)</i>`,
    cancelKeyboard()
  );
}

async function handleAddChannelText(ctx) {
  const userId = ctx.from.id;
  const userState = getState(userId);
  if (!userState) return false;

  const text = (ctx.message.text || "").trim();

  if (text === "❌ Bekor qilish") {
    clearState(userId);
    await ctx.reply("Kanal qo'shish bekor qilindi.", adminMainKeyboard());
    return true;
  }

  // 1. Sarlavha
  if (userState.state === "ADD_CH_TITLE") {
    const chType = userState.data.chType;
    updateData(userId, { title: text });

    if (chType === "external") {
      updateData(userId, { channelId: null });
      setState(userId, "ADD_CH_URL", userState.data);
      updateData(userId, { title: text, channelId: null });
      await ctx.replyWithHTML(
        "2️⃣ Endi to'liq veb-havolani (URL) kiriting:\n" +
        "<i>(Masalan: https://example.com yoki https://instagram.com/...)</i>",
        cancelKeyboard()
      );
    } else {
      setState(userId, "ADD_CH_ID", userState.data);
      updateData(userId, { title: text });
      await ctx.replyWithHTML(
        "2️⃣ Kanalning Telegram ID si yoki @username sini kiriting:\n" +
        "<i>(Masalan: -1001234567890 yoki @kanal_username)</i>\n\n" +
        "⚠️ <b>Muhim:</b> Bot ushbu kanalda administrator bo'lishi shart!",
        cancelKeyboard()
      );
    }
    return true;
  }

  // 2. Chat ID
  if (userState.state === "ADD_CH_ID") {
    let channelId = text;
    if ((text.startsWith("-") && /^\d+$/.test(text.slice(1))) || /^\d+$/.test(text)) {
      channelId = parseInt(text, 10);
    }

    try {
      const chat = await ctx.telegram.getChat(channelId);
      channelId = chat.id;
    } catch (e) {}

    updateData(userId, { channelId });
    setState(userId, "ADD_CH_URL", userState.data);
    updateData(userId, { channelId });

    await ctx.replyWithHTML(
      "3️⃣ Endi foydalanuvchilar o'tishi uchun kanal havolasini (linkini) kiriting:\n" +
      "<i>(Masalan: https://t.me/joinchat/... yoki https://t.me/+AbCdEf...)</i>",
      cancelKeyboard()
    );
    return true;
  }

  // 3. URL
  if (userState.state === "ADD_CH_URL") {
    if (!text.startsWith("http://") && !text.startsWith("https://") && !text.startsWith("t.me")) {
      await ctx.reply("⚠️ Iltimos, haqiqiy URL manzil kiriting (https://...):");
      return true;
    }

    const { title, chType, channelId } = userState.data;
    const btnName = "< Obuna bo'lish >";

    await Channel.create({
      title,
      type: chType,
      channelId,
      url: text,
      buttonName: btnName
    });

    clearState(userId);
    await ctx.replyWithHTML(
      `✅ <b>Kanal muvaffaqiyatli ulandi!</b>\n\n` +
      `📌 Nomi: <b>${title}</b>\n` +
      `🔖 Turi: <code>${chType}</code>\n` +
      `🔗 Havola: ${text}\n` +
      `🔘 Tugma nomi: <b>${btnName}</b>`,
      adminMainKeyboard()
    );
    return true;
  }

  return false;
}

async function handleManageChannels(ctx) {
  const channels = await Channel.find();
  if (!channels || channels.length === 0) {
    return ctx.reply("Hozircha ulangan majburiy kanallar yo'q.");
  }

  await ctx.replyWithHTML(
    "⚙️ <b>Ulangan kanallar ro'yxati:</b>\n\nO'chirmoqchi bo'lgan kanalingiz ustiga bosing:",
    manageChannelsKeyboard(channels)
  );
}

async function handleDeleteChannel(ctx) {
  const chId = ctx.match[1];
  const channel = await Channel.findById(chId);
  const title = channel ? channel.title : "Kanal";

  await Channel.findByIdAndDelete(chId);
  await ctx.answerCbQuery(`'${title}' o'chirildi!`, { show_alert: true });

  const channels = await Channel.find();
  if (channels && channels.length > 0) {
    await ctx.editMessageText(
      "⚙️ <b>Ulangan kanallar ro'yxati:</b>\n\nO'chirmoqchi bo'lgan kanalingiz ustiga bosing:",
      { parse_mode: "HTML", ...manageChannelsKeyboard(channels) }
    );
  } else {
    await ctx.editMessageText("Barcha kanallar o'chirildi.");
  }
}

module.exports = {
  handleStartAddChannel,
  handleChooseChannelType,
  handleAddChannelText,
  handleManageChannels,
  handleDeleteChannel
};
