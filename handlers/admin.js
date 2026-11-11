const { getStatistics } = require("../database");
const config = require("../config");
const { adminMainKeyboard, mainMenuKeyboard } = require("../keyboards/keyboards");
const { clearState } = require("../state");

function isAdmin(userId) {
  return config.ADMINS.includes(userId);
}

async function handleAdminCommand(ctx) {
  const userId = ctx.from.id;
  if (!isAdmin(userId)) return;

  clearState(userId);
  const text = (
    "👑 <b>Admin Boshqaruv Paneliga Xush Kelibsiz!</b>\n\n" +
    "Quyidagi bo'limlardan birini tanlang:"
  );
  await ctx.replyWithHTML(text, adminMainKeyboard());
}

async function handleBackToUserMode(ctx) {
  clearState(ctx.from.id);
  await ctx.reply("Siz foydalanuvchi menyusiga o'tdingiz.", mainMenuKeyboard());
}

async function handleStatistics(ctx) {
  if (!isAdmin(ctx.from.id)) return;

  const stats = await getStatistics();
  const now = new Date().toLocaleString("uz-UZ");

  const text = (
    `📊 <b>Bot Statistikasi:</b>\n` +
    `<i>(Holat: ${now})</i>\n\n` +
    `👥 <b>Jami foydalanuvchilar:</b> ${stats.totalUsers.toLocaleString()} ta\n` +
    `✅ <b>Faol (Active) foydalanuvchilar:</b> ${stats.activeUsers.toLocaleString()} ta\n` +
    `🚫 <b>Bloklagan foydalanuvchilar:</b> ${stats.blockedUsers.toLocaleString()} ta\n` +
    `📅 <b>Bugun qo'shilganlar:</b> ${stats.todayUsers.toLocaleString()} ta\n\n` +
    `📢 <b>Ulangan majburiy kanallar:</b> ${stats.totalChannels.toLocaleString()} ta\n` +
    `📋 <b>Faol vazifalar soni:</b> ${stats.totalTasks.toLocaleString()} ta`
  );

  await ctx.replyWithHTML(text);
}

async function handleAdminCancelCallback(ctx) {
  clearState(ctx.from.id);
  try {
    await ctx.deleteMessage();
  } catch (e) {}
  await ctx.reply("Amal bekor qilindi.", adminMainKeyboard());
}

async function handleAdminCloseCallback(ctx) {
  try {
    await ctx.deleteMessage();
  } catch (e) {}
}

module.exports = {
  isAdmin,
  handleAdminCommand,
  handleBackToUserMode,
  handleStatistics,
  handleAdminCancelCallback,
  handleAdminCloseCallback
};
