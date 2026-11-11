const { Task, UserTask, User, JoinRequest } = require("../database");
const { tasksListKeyboard, taskActionKeyboard } = require("../keyboards/keyboards");
const { isSubscribedToChat } = require("../services/checker");

async function handleViewTasks(ctx) {
  const tasks = await Task.find({ isActive: true });
  if (!tasks || tasks.length === 0) {
    return ctx.answerCbQuery("Hozircha hech qanday faol vazifa mavjud emas.", { show_alert: true });
  }

  const text = (
    "📋 <b>Mavjud vazifalar ro'yxati:</b>\n\n" +
    "Vazifalarni bajarib, hisobingizga pul ishlang!\n" +
    "<i>Har bir vazifani tanlab, shartlarini bajaring.</i>\n\n" +
    "⚠️ <b>Eslatma:</b> 30 kun ichida kanaldan yoki guruhdan chiqib ketsangiz, " +
    "balansingizdan <b>vazifa narxi + 250 UZS</b> jarima yechiladi!"
  );

  await ctx.editMessageText(text, {
    parse_mode: "HTML",
    ...tasksListKeyboard(tasks)
  });
}

async function handleSingleTaskView(ctx) {
  const taskId = ctx.match[1];
  const task = await Task.findById(taskId);

  if (!task || !task.isActive) {
    return ctx.answerCbQuery("Bu vazifa endi faol emas!", { show_alert: true });
  }

  const userId = ctx.from.id;
  const alreadyDone = await UserTask.findOne({ userId, taskId });

  const typeTitles = {
    channel: "📢 Telegram kanalga obuna bo'lish",
    group: "👥 Telegram guruhga a'zo bo'lish",
    join_request: "📥 Zayafkali kanalga kirish so'rovi yuborish"
  };
  const taskTypeText = typeTitles[task.taskType] || "Obuna bo'lish";
  const reward = task.reward || 0;

  if (alreadyDone) {
    const text = (
      `✅ <b>${task.title}</b>\n\n` +
      `📌 Turi: ${taskTypeText}\n` +
      `💰 Mukofot: <b>+${reward.toLocaleString()} UZS</b>\n\n` +
      `<i>Siz bu vazifani allaqachon bajargansiz va mukofotni olgansiz!</i>`
    );
    const tasks = await Task.find({ isActive: true });
    return ctx.editMessageText(text, {
      parse_mode: "HTML",
      ...tasksListKeyboard(tasks)
    });
  }

  const text = (
    `📋 <b>Vazifa:</b> ${task.title}\n\n` +
    `📌 <b>Shart:</b> ${taskTypeText}\n` +
    `💵 <b>Mukofot:</b> <b>+${reward.toLocaleString()} UZS</b>\n\n` +
    `<i>Kanalga/guruhga o'ting, obuna bo'ling va 'Vazifani tekshirish' tugmasini bosing!</i>\n\n` +
    `⚠️ <b>Qoida:</b> 30 kun ichida chiqib ketmasligingiz shart (jarima: vazifa narxi + 250 UZS)!`
  );

  await ctx.editMessageText(text, {
    parse_mode: "HTML",
    ...taskActionKeyboard(task.url || "https://t.me", taskId)
  });
}

async function handleCheckSingleTask(ctx) {
  const taskId = ctx.match[1];
  const task = await Task.findById(taskId);

  if (!task) {
    return ctx.answerCbQuery("Vazifa topilmadi!", { show_alert: true });
  }

  const userId = ctx.from.id;
  const alreadyDone = await UserTask.findOne({ userId, taskId });
  if (alreadyDone) {
    return ctx.answerCbQuery("Siz bu vazifani allaqachon bajargansiz!", { show_alert: true });
  }

  const { taskType, channelId, reward } = task;
  let isCompleted = false;

  if (taskType === "channel" || taskType === "group") {
    if (channelId) {
      isCompleted = await isSubscribedToChat(ctx.telegram, channelId, userId);
    }
  } else if (taskType === "join_request") {
    if (channelId) {
      const intId = parseInt(channelId, 10);
      if (!isNaN(intId)) {
        const req = await JoinRequest.findOne({ userId, channelId: intId });
        if (req) isCompleted = true;
      }
      if (!isCompleted) {
        isCompleted = await isSubscribedToChat(ctx.telegram, channelId, userId);
      }
    }
  }

  if (!isCompleted) {
    return ctx.answerCbQuery(
      "❌ Siz hali vazifani bajarmadingiz!\nIltimos, havola orqali a'zo bo'ling yoki so'rov yuboring.",
      { show_alert: true }
    );
  }

  // Bajarildi
  await UserTask.create({
    userId,
    taskId,
    channelId,
    reward,
    penalized: false,
    completedAt: new Date()
  });

  await User.updateOne({ userId }, { $inc: { balance: reward } });
  await ctx.answerCbQuery("🎉 Tabriklaymiz, vazifa muvaffaqiyatli bajarildi!");

  const text = (
    `🎉 <b>Tabriklaymiz!</b>\n\n` +
    `Siz '<b>${task.title}</b>' vazifasini muvaffaqiyatli bajardingiz!\n` +
    `Balansingizga <b>+${reward.toLocaleString()} UZS</b> qo'shildi! 💰\n\n` +
    `⚠️ <b>Eslatma:</b> 30 kun ichida a'zolikni bekor qilsangiz, balansingizdan ` +
    `<b>${(reward + 250).toLocaleString()} UZS</b> (vazifa narxi + 250 UZS) jarima yechib olinadi.`
  );

  const tasks = await Task.find({ isActive: true });
  await ctx.editMessageText(text, {
    parse_mode: "HTML",
    ...tasksListKeyboard(tasks)
  });
}

module.exports = {
  handleViewTasks,
  handleSingleTaskView,
  handleCheckSingleTask
};
