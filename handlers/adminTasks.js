const { Task, getSetting } = require("../database");
const { taskTypeInlineKb, manageTasksKeyboard, adminMainKeyboard, cancelKeyboard } = require("../keyboards/keyboards");
const { getState, setState, clearState, updateData } = require("../state");

function escapeHTML(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

async function handleStartAddTask(ctx) {
  clearState(ctx.from.id);
  await ctx.replyWithHTML(
    "📋 <b>Yangi vazifa qo'shish bo'limi</b>\n\n" +
    "Vazifa turini tanlang:\n" +
    "<i>(Telegram kanal, guruh yoki zayafkali kanal)</i>",
    taskTypeInlineKb()
  );
}

async function handleChooseTaskType(ctx) {
  const taskType = ctx.match[1];
  const userId = ctx.from.id;

  setState(userId, "ADD_TASK_TITLE", { taskType });

  const typeDescs = {
    channel: "Telegram kanal",
    group: "Telegram guruh",
    join_request: "Zayafkali kanal"
  };

  try {
    await ctx.deleteMessage();
  } catch (e) {}

  await ctx.replyWithHTML(
    `Tanlangan vazifa turi: <b>${typeDescs[taskType] || taskType}</b>\n\n` +
    `1️⃣ Vazifa uchun nom (sarlavha) kiriting:\n` +
    `<i>(Masalan: Rasmiy guruhimizga a'zo bo'ling)</i>`,
    cancelKeyboard()
  );
}

async function handleAddTaskText(ctx) {
  const userId = ctx.from.id;
  const userState = getState(userId);
  if (!userState) return false;

  const text = (ctx.message.text || "").trim();

  if (text === "❌ Bekor qilish") {
    clearState(userId);
    await ctx.reply("Vazifa qo'shish bekor qilindi.", adminMainKeyboard());
    return true;
  }

  // 1. Sarlavha
  if (userState.state === "ADD_TASK_TITLE") {
    updateData(userId, { title: text });
    setState(userId, "ADD_TASK_ID", userState.data);
    updateData(userId, { title: text });

    await ctx.replyWithHTML(
      "2️⃣ Kanal yoki guruhning Telegram ID sini yoki @username sini kiriting:\n" +
      "<i>(Masalan: -1009876543210 yoki @guruh_nomi)</i>\n\n" +
      "⚠️ <b>Eslatma:</b> Bot kanalda/guruhda administrator bo'lishi kerak!",
      cancelKeyboard()
    );
    return true;
  }

  // 2. Chat ID
  if (userState.state === "ADD_TASK_ID") {
    let channelId = text;
    if ((text.startsWith("-") && /^\d+$/.test(text.slice(1))) || /^\d+$/.test(text)) {
      channelId = parseInt(text, 10);
    }

    try {
      const chat = await ctx.telegram.getChat(channelId);
      channelId = chat.id;
    } catch (e) {}

    updateData(userId, { channelId });
    setState(userId, "ADD_TASK_URL", userState.data);
    updateData(userId, { channelId });

    await ctx.replyWithHTML(
      "3️⃣ Kanal yoki guruh havolasini (linkini) kiriting:\n" +
      "<i>(Masalan: https://t.me/guruh_nomi yoki https://t.me/+AbcDeF...)</i>",
      cancelKeyboard()
    );
    return true;
  }

  // 3. Havola (URL)
  if (userState.state === "ADD_TASK_URL") {
    const defaultPrice = (await getSetting("task_price")) || 500;
    updateData(userId, { url: text });
    setState(userId, "ADD_TASK_REWARD", userState.data);
    updateData(userId, { url: text });

    await ctx.replyWithHTML(
      `4️⃣ Ushbu vazifani bajargan foydalanuvchiga beriladigan mukofot summasini kiriting (UZS):\n` +
      `<i>(Standart: ${defaultPrice.toLocaleString()} UZS)</i>`,
      cancelKeyboard()
    );
    return true;
  }

  // 4. Mukofot summasi
  if (userState.state === "ADD_TASK_REWARD") {
    const cleanNum = text.replace(/\s+/g, "").replace(/,/g, "");
    const defaultPrice = (await getSetting("task_price")) || 500;
    const reward = /^\d+$/.test(cleanNum) ? parseInt(cleanNum, 10) : defaultPrice;

    const { title, taskType, channelId, url } = userState.data;

    await Task.create({
      title,
      taskType,
      channelId,
      url,
      reward,
      isActive: true
    });

    clearState(userId);
    const safeTitle = escapeHTML(title);
    const safeType = escapeHTML(taskType);
    const safeUrl = escapeHTML(url);

    try {
      await ctx.replyWithHTML(
        `✅ <b>Yangi vazifa muvaffaqiyatli qo'shildi!</b>\n\n` +
        `📌 Nomi: <b>${safeTitle}</b>\n` +
        `🔖 Turi: <code>${safeType}</code>\n` +
        `💰 Mukofot: <b>${reward.toLocaleString()} UZS</b>\n` +
        `🔗 Havola: ${safeUrl}`,
        adminMainKeyboard()
      );
    } catch (e) {
      await ctx.reply(
        `✅ Yangi vazifa muvaffaqiyatli qo'shildi!\n\n` +
        `📌 Nomi: ${title}\n` +
        `🔖 Turi: ${taskType}\n` +
        `💰 Mukofot: ${reward.toLocaleString()} UZS\n` +
        `🔗 Havola: ${url}`,
        adminMainKeyboard()
      );
    }
    return true;
  }

  return false;
}

async function handleManageTasks(ctx) {
  const tasks = await Task.find({ isActive: true });
  if (!tasks || tasks.length === 0) {
    return ctx.reply("Hozircha faol vazifalar mavjud emas.");
  }

  await ctx.replyWithHTML(
    "🗂 <b>Faol vazifalar ro'yxati:</b>\n\nO'chirmoqchi bo'lgan vazifangiz ustiga bosing:",
    manageTasksKeyboard(tasks)
  );
}

async function handleDeleteTask(ctx) {
  const tId = ctx.match[1];
  const task = await Task.findById(tId);
  const title = task ? task.title : "Vazifa";

  await Task.findByIdAndDelete(tId);
  await ctx.answerCbQuery(`'${title}' o'chirildi!`, { show_alert: true });

  const tasks = await Task.find({ isActive: true });
  if (tasks && tasks.length > 0) {
    await ctx.editMessageText(
      "🗂 <b>Faol vazifalar ro'yxati:</b>\n\nO'chirmoqchi bo'lgan vazifangiz ustiga bosing:",
      { parse_mode: "HTML", ...manageTasksKeyboard(tasks) }
    );
  } else {
    await ctx.editMessageText("Barcha vazifalar o'chirildi.");
  }
}

module.exports = {
  handleStartAddTask,
  handleChooseTaskType,
  handleAddTaskText,
  handleManageTasks,
  handleDeleteTask
};
