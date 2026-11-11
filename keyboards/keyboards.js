const { Markup } = require("telegraf");

function contactKeyboard() {
  return Markup.keyboard([
    [Markup.button.contactRequest("📱 Kontaktni ulashish")]
  ]).resize().oneTime();
}

function mainMenuKeyboard() {
  return Markup.keyboard([
    ["📹 Video qo'llanma"],
    ["👤 Kabinet", "🔗 Taklif havola"],
    ["📢 Reklama", "ℹ️ Bot haqida"],
    ["🆘 Yordam"]
  ]).resize();
}

function cancelKeyboard() {
  return Markup.keyboard([["❌ Bekor qilish"]]).resize();
}

function yesNoKeyboard() {
  return Markup.keyboard([["✅ Ha", "❌ Yo'q"]]).resize();
}

function mandatoryChannelsKeyboard(unsubscribedChannels) {
  const buttons = [];
  for (const ch of unsubscribedChannels) {
    const url = ch.url || "https://t.me";
    const btnName = ch.buttonName || "< Obuna bo'lish >";
    buttons.push([Markup.button.url(btnName, url)]);
  }
  buttons.push([Markup.button.callback("✅ Obunani tekshirish", "check_subscription")]);
  return Markup.inlineKeyboard(buttons);
}

function cabinetKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback("💳 Hisobni to'ldirish", "top_up_balance"),
      Markup.button.callback("📋 Vazifalar", "view_tasks")
    ]
  ]);
}

function quickFillBalanceKeyboard() {
  return Markup.inlineKeyboard([
    [Markup.button.callback("💳 Hisobni to'ldirish", "top_up_balance")]
  ]);
}

function paymentConfirmKeyboard(paymentId) {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback("✅ Tasdiqlash", `pay_approve:${paymentId}`),
      Markup.button.callback("❌ Bekor qilish", `pay_reject:${paymentId}`)
    ]
  ]);
}

function tasksListKeyboard(tasks) {
  const buttons = tasks.map((t, index) => [
    Markup.button.callback(
      `${index + 1}. ${t.title} (+${t.reward.toLocaleString()} UZS)`,
      `task_view:${t._id}`
    )
  ]);
  return Markup.inlineKeyboard(buttons);
}

function taskActionKeyboard(taskUrl, taskId) {
  return Markup.inlineKeyboard([
    [Markup.button.url("🔗 O'tish va obuna bo'lish", taskUrl)],
    [Markup.button.callback("✅ Vazifani tekshirish", `task_check:${taskId}`)],
    [Markup.button.callback("🔙 Vazifalar ro'yxati", "view_tasks")]
  ]);
}

function shareReferralKeyboard(botUsername, userId) {
  const refLink = `https://t.me/${botUsername}?start=ref_${userId}`;
  const shareText = `🔥 Zo'r bot topdim! Video qo'llanmalar, vazifalar va daromad olish imkoniyati!\nHoziroq kiring: ${refLink}`;
  const encoded = encodeURIComponent(shareText);
  const shareUrl = `https://t.me/share/url?url=${refLink}&text=${encoded}`;

  return Markup.inlineKeyboard([
    [Markup.button.url("📤 Do'stlarga ulashish", shareUrl)]
  ]);
}

function customAdKeyboard(buttonText, buttonUrl) {
  return Markup.inlineKeyboard([
    [Markup.button.url(buttonText, buttonUrl)]
  ]);
}

function adminMainKeyboard() {
  return Markup.keyboard([
    ["📢 Kanal ulash", "⚙️ Kanallarni boshqarish"],
    ["📊 Statistika", "✉️ Xabar yuborish"],
    ["📹 Video joylash", "📢 Reklama joylash"],
    ["📋 Vazifa qo'shish", "🗂 Vazifalarni boshqarish"],
    ["💰 Referal narxi", "💵 Vazifa narxi"],
    ["💳 Karta ma'lumotlari"],
    ["ℹ️ Bot haqida matni", "🆘 Yordam matni"],
    ["🔙 Foydalanuvchi rejimi"]
  ]).resize();
}

function channelTypeInlineKb() {
  return Markup.inlineKeyboard([
    [Markup.button.callback("📢 Ochiq kanal (@username)", "ch_type:public")],
    [Markup.button.callback("🔒 Shaxsiy (Private) kanal", "ch_type:private")],
    [Markup.button.callback("📥 Zayafkali kanal (Join request)", "ch_type:join_request")],
    [Markup.button.callback("🌐 Tashqi link (Web havola)", "ch_type:external")],
    [Markup.button.callback("❌ Bekor qilish", "admin_cancel")]
  ]);
}

function taskTypeInlineKb() {
  return Markup.inlineKeyboard([
    [Markup.button.callback("📢 Telegram kanal", "task_type:channel")],
    [Markup.button.callback("👥 Telegram guruh", "task_type:group")],
    [Markup.button.callback("📥 Zayafkali kanal", "task_type:join_request")],
    [Markup.button.callback("❌ Bekor qilish", "admin_cancel")]
  ]);
}

function manageChannelsKeyboard(channels) {
  const buttons = channels.map((ch) => [
    Markup.button.callback(`🗑 ${ch.title} (${ch.type})`, `del_channel:${ch._id}`)
  ]);
  buttons.push([Markup.button.callback("🔙 Yopish", "admin_close")]);
  return Markup.inlineKeyboard(buttons);
}

function manageTasksKeyboard(tasks) {
  const buttons = tasks.map((t) => [
    Markup.button.callback(`🗑 ${t.title} (${t.reward.toLocaleString()} UZS)`, `del_task:${t._id}`)
  ]);
  buttons.push([Markup.button.callback("🔙 Yopish", "admin_close")]);
  return Markup.inlineKeyboard(buttons);
}

function broadcastConfirmKeyboard() {
  return Markup.inlineKeyboard([
    [
      Markup.button.callback("🚀 Yuborishni boshlash", "broadcast_confirm"),
      Markup.button.callback("❌ Bekor qilish", "broadcast_cancel")
    ]
  ]);
}

module.exports = {
  contactKeyboard,
  mainMenuKeyboard,
  cancelKeyboard,
  yesNoKeyboard,
  mandatoryChannelsKeyboard,
  cabinetKeyboard,
  quickFillBalanceKeyboard,
  paymentConfirmKeyboard,
  tasksListKeyboard,
  taskActionKeyboard,
  shareReferralKeyboard,
  customAdKeyboard,
  adminMainKeyboard,
  channelTypeInlineKb,
  taskTypeInlineKb,
  manageChannelsKeyboard,
  manageTasksKeyboard,
  broadcastConfirmKeyboard
};
