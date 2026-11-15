const express = require("express");
const { Telegraf } = require("telegraf");
const cron = require("node-cron");

const config = require("./config");
const { connectDB } = require("./database");
const { checkPenalties } = require("./services/penalty");

// Handlers
const { handleStart, handleContact, handleCheckSubscription } = require("./handlers/start");
const {
  handleVideoGuide,
  handleCabinet,
  handleReferral,
  handleAdSection,
  handleAbout,
  handleHelp
} = require("./handlers/userMenu");
const {
  handleTopUpCallback,
  handlePaymentText,
  handleReceipt,
  handleApprovePayment,
  handleRejectPayment
} = require("./handlers/payment");
const {
  handleViewTasks,
  handleSingleTaskView,
  handleCheckSingleTask
} = require("./handlers/tasks");
const {
  isAdmin,
  handleAdminCommand,
  handleBackToUserMode,
  handleStatistics,
  handleAdminCancelCallback,
  handleAdminCloseCallback
} = require("./handlers/admin");
const {
  handleStartAddChannel,
  handleChooseChannelType,
  handleAddChannelText,
  handleManageChannels,
  handleDeleteChannel
} = require("./handlers/adminChannels");
const {
  handleStartAddTask,
  handleChooseTaskType,
  handleAddTaskText,
  handleManageTasks,
  handleDeleteTask
} = require("./handlers/adminTasks");
const {
  handleStartBroadcast,
  handleBroadcastInput,
  handleBroadcastConfirm,
  handleBroadcastCancel
} = require("./handlers/adminBroadcast");
const {
  handleStartSetRefPrice,
  handleStartSetTaskPrice,
  handleStartSetCard,
  handleStartSetVideoGuide,
  handleStartSetAd,
  handleStartSetAbout,
  handleStartSetHelp,
  handleStartSetDatabaseChannel,
  handleAdminSettingsInput
} = require("./handlers/adminSettings");
const { handleChatJoinRequest, handleMyChatMember } = require("./handlers/events");

if (!config.BOT_TOKEN) {
  console.error("BOT_TOKEN ko'rsatilmagan! Iltimos, .env faylini tekshiring.");
  process.exit(1);
}

const bot = new Telegraf(config.BOT_TOKEN);

// Express Health Check server (Render.com port binding uchun)
const app = express();
app.get("/", (req, res) => res.send("OK - Anti Spam Bot is running (Node.js)!"));
app.get("/health", (req, res) => res.json({ status: "ok", time: new Date() }));

app.listen(config.PORT, () => {
  console.log(`Express server ${config.PORT} portida tinglamoqda (Render.com)`);
});

// --- TELEGRAM EVENTS ---
bot.on("chat_join_request", handleChatJoinRequest);
bot.on("my_chat_member", handleMyChatMember);

// --- START & CONTACT ---
bot.start(handleStart);
bot.on("contact", handleContact);
bot.action("check_subscription", handleCheckSubscription);

// --- FOYDALANUVCHI INTERFEYSI MENYULARI ---
bot.hears("📹 Video qo'llanma", handleVideoGuide);
bot.hears("👤 Kabinet", handleCabinet);
bot.hears("🔗 Taklif havola", handleReferral);
bot.hears("📢 Reklama", handleAdSection);
bot.hears("ℹ️ Bot haqida", handleAbout);
bot.hears("🆘 Yordam", handleHelp);

// --- KABINET VA TO'LOV CALLBACKLARI ---
bot.action("top_up_balance", handleTopUpCallback);
bot.action(/^pay_approve:(.+)$/, handleApprovePayment);
bot.action(/^pay_reject:(.+)$/, handleRejectPayment);

// --- VAZIFALAR CALLBACKLARI ---
bot.action("view_tasks", handleViewTasks);
bot.action(/^task_view:(.+)$/, handleSingleTaskView);
bot.action(/^task_check:(.+)$/, handleCheckSingleTask);

// --- ADMIN PANELI ---
bot.command("admin", handleAdminCommand);
bot.hears("🔙 Foydalanuvchi rejimi", handleBackToUserMode);
bot.hears("📊 Statistika", handleStatistics);
bot.action("admin_cancel", handleAdminCancelCallback);
bot.action("admin_close", handleAdminCloseCallback);

// Admin: Kanal boshqaruvi
bot.hears("📢 Kanal ulash", (ctx) => isAdmin(ctx.from.id) && handleStartAddChannel(ctx));
bot.action(/^ch_type:(.+)$/, (ctx) => isAdmin(ctx.from.id) && handleChooseChannelType(ctx));
bot.hears("⚙️ Kanallarni boshqarish", (ctx) => isAdmin(ctx.from.id) && handleManageChannels(ctx));
bot.action(/^del_channel:(.+)$/, (ctx) => isAdmin(ctx.from.id) && handleDeleteChannel(ctx));

// Admin: Vazifalar boshqaruvi
bot.hears("📋 Vazifa qo'shish", (ctx) => isAdmin(ctx.from.id) && handleStartAddTask(ctx));
bot.action(/^task_type:(.+)$/, (ctx) => isAdmin(ctx.from.id) && handleChooseTaskType(ctx));
bot.hears("🗂 Vazifalarni boshqarish", (ctx) => isAdmin(ctx.from.id) && handleManageTasks(ctx));
bot.action(/^del_task:(.+)$/, (ctx) => isAdmin(ctx.from.id) && handleDeleteTask(ctx));

// Admin: Xabar yuborish (Rassilka)
bot.hears("✉️ Xabar yuborish", (ctx) => isAdmin(ctx.from.id) && handleStartBroadcast(ctx));
bot.action("broadcast_confirm", (ctx) => isAdmin(ctx.from.id) && handleBroadcastConfirm(ctx));
bot.action("broadcast_cancel", (ctx) => isAdmin(ctx.from.id) && handleBroadcastCancel(ctx));

// Admin: Sozlamalar
bot.hears("💰 Referal narxi", (ctx) => isAdmin(ctx.from.id) && handleStartSetRefPrice(ctx));
bot.hears("💵 Vazifa narxi", (ctx) => isAdmin(ctx.from.id) && handleStartSetTaskPrice(ctx));
bot.hears("💳 Karta ma'lumotlari", (ctx) => isAdmin(ctx.from.id) && handleStartSetCard(ctx));
bot.hears("📁 Baza kanali", (ctx) => isAdmin(ctx.from.id) && handleStartSetDatabaseChannel(ctx));
bot.hears("📹 Video joylash", (ctx) => isAdmin(ctx.from.id) && handleStartSetVideoGuide(ctx));
bot.hears("📢 Reklama joylash", (ctx) => isAdmin(ctx.from.id) && handleStartSetAd(ctx));
bot.hears("ℹ️ Bot haqida matni", (ctx) => isAdmin(ctx.from.id) && handleStartSetAbout(ctx));
bot.hears("🆘 Yordam matni", (ctx) => isAdmin(ctx.from.id) && handleStartSetHelp(ctx));

// --- MATN VA MEDIA KIRISHLARINI QAYTA ISHLASH (FSM) ---
bot.on(["text"], async (ctx, next) => {
  const userId = ctx.from.id;

  // 1. To'lov matnlari
  const handledPayment = await handlePaymentText(ctx);
  if (handledPayment) return;

  // 2. Admin kanal qo'shish
  if (isAdmin(userId)) {
    const handledChannel = await handleAddChannelText(ctx);
    if (handledChannel) return;

    // 3. Admin vazifa qo'shish
    const handledTask = await handleAddTaskText(ctx);
    if (handledTask) return;

    // 4. Admin xabar yuborish
    const handledBroadcast = await handleBroadcastInput(ctx);
    if (handledBroadcast) return;

    // 5. Admin sozlamalar
    const handledSettings = await handleAdminSettingsInput(ctx);
    if (handledSettings) return;
  }

  return next();
});

// To'lov cheki yoki admin media yuklashlari
bot.on(["photo", "document", "video"], async (ctx, next) => {
  const userId = ctx.from.id;

  // Foydalanuvchi chek yuborishi
  const handledReceipt = await handleReceipt(ctx);
  if (handledReceipt) return;

  // Admin media (reklama, video qo'llanma, xabar yuborish)
  if (isAdmin(userId)) {
    const handledBroadcast = await handleBroadcastInput(ctx);
    if (handledBroadcast) return;

    const handledSettings = await handleAdminSettingsInput(ctx);
    if (handledSettings) return;
  }

  return next();
});

// --- ASOSIY ISHGA TUSHIRISH ---
async function bootstrap() {
  await connectDB();

  // Har 1 soatda 30 kunlik vazifa jarimalarini tekshirish (0-daqiqada)
  cron.schedule("0 * * * *", () => {
    checkPenalties(bot.telegram);
  });

  bot.launch({
    allowedUpdates: [
      "message",
      "callback_query",
      "chat_join_request",
      "my_chat_member",
      "chat_member"
    ]
  }).then(async () => {
    const me = await bot.telegram.getMe();
    console.log(`Bot muvaffaqiyatli ishga tushdi: @${me.username}`);
  }).catch((err) => {
    console.error("Botni ishga tushirishda xatolik:", err);
  });

  process.once("SIGINT", () => bot.stop("SIGINT"));
  process.once("SIGTERM", () => bot.stop("SIGTERM"));
}

bootstrap();
