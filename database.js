const mongoose = require("mongoose");
const config = require("./config");
const User = require("./models/User");
const Channel = require("./models/Channel");
const JoinRequest = require("./models/JoinRequest");
const Task = require("./models/Task");
const UserTask = require("./models/UserTask");
const Payment = require("./models/Payment");
const Setting = require("./models/Setting");

async function connectDB() {
  try {
    await mongoose.connect(config.MONGO_URI);
    console.log("MongoDB ga muvaffaqiyatli ulanildi!");
    await ensureDefaultSettings();
  } catch (error) {
    console.error("MongoDB ulanishida xatolik:", error);
    process.exit(1);
  }
}

async function ensureDefaultSettings() {
  const defaults = {
    referral_price: config.DEFAULT_REFERRAL_PRICE,
    task_price: config.DEFAULT_TASK_PRICE,
    database_channel: "",
    card_number: "8600 0000 0000 0000",
    card_holder: "ADMIN CARD",
    video_guide: {
      file_id: null,
      caption: "📹 Maxsus video qo'llanma!\nUshbu qo'llanmada barcha zarur ko'rsatmalar berilgan."
    },
    ad_post: {
      text: "📢 Bu yerda sizning reklamangiz bo'lishi mumkin!\nReklama joylashtirish uchun adminga murojaat qiling.",
      file_id: null,
      file_type: null,
      has_button: false,
      button_text: null,
      button_url: null
    },
    about_text: (
      "🤖 <b>Bot haqida</b>\n\n" +
      "Bu bot orqali siz qulay va oson tarzda video qo'llanmalarni olishingiz, " +
      "vazifalarni bajarib pul ishlashingiz, do'stlaringizni taklif qilib " +
      "balansingizni oshirishingiz mumkin!\n\n" +
      "🌟 <b>Afzalliklari:</b>\n" +
      "• Tezkor va xavfsiz to'lovlar\n" +
      "• Qiziqarli va daromadli vazifalar\n" +
      "• Foydali video qo'llanmalar\n" +
      "• 24/7 faol tizim"
    ),
    help_text: (
      "🆘 <b>Yordam va Murojaat</b>\n\n" +
      "Savol, taklif yoki to'lov bo'yicha muammo bormi?\n" +
      "Admin bilan bog'lanish: @admin\n" +
      "Biz sizga doim yordam berishga tayyormiz!"
    )
  };

  for (const [key, value] of Object.entries(defaults)) {
    const existing = await Setting.findOne({ key });
    if (!existing) {
      await Setting.create({ key, value });
    }
  }
}

// User Helpers
async function getOrCreateUser(userId, firstName, lastName = "", username = "", referrerId = null) {
  let user = await User.findOne({ userId });
  if (!user) {
    user = await User.create({
      userId,
      firstName: firstName || "",
      lastName: lastName || "",
      username: username || "",
      referrerId: referrerId || null,
      createdAt: new Date()
    });
  } else {
    user.firstName = firstName || user.firstName;
    user.lastName = lastName || user.lastName;
    user.username = username || user.username;
    user.isActive = true;
    await user.save();
  }
  return user;
}

async function getSetting(key) {
  const doc = await Setting.findOne({ key });
  return doc ? doc.value : null;
}

async function setSetting(key, value) {
  await Setting.findOneAndUpdate({ key }, { value }, { upsert: true, new: true });
}

async function getStatistics() {
  const totalUsers = await User.countDocuments();
  const activeUsers = await User.countDocuments({ isActive: true });
  const blockedUsers = await User.countDocuments({ isActive: false });

  const now = new Date();
  const startOfDay = new Date(now.getFullYear(), now.month || now.getMonth(), now.getDate());
  const todayUsers = await User.countDocuments({ createdAt: { $gte: startOfDay } });

  const totalChannels = await Channel.countDocuments();
  const totalTasks = await Task.countDocuments({ isActive: true });

  return {
    totalUsers,
    activeUsers,
    blockedUsers,
    todayUsers,
    totalChannels,
    totalTasks
  };
}

module.exports = {
  connectDB,
  User,
  Channel,
  JoinRequest,
  Task,
  UserTask,
  Payment,
  Setting,
  getOrCreateUser,
  getSetting,
  setSetting,
  getStatistics
};
