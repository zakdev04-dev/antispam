require("dotenv").config();

const BOT_TOKEN = process.env.BOT_TOKEN || process.env.DOT_TOKEN || "";
const MONGO_URI = process.env.MONGO_URI || "mongodb://localhost:27017/anti_spam_bot";
const PORT = parseInt(process.env.PORT || "8080", 10);

const ADMINS_RAW = process.env.ADMINS || process.env.ADMIN_ID || "";
const ADMINS = ADMINS_RAW.split(",")
  .map((id) => id.trim())
  .filter((id) => /^\d+$/.test(id))
  .map((id) => parseInt(id, 10));

const VIDEO_PRICE = parseInt(process.env.VIDEO_PRICE || "15000", 10);
const PENALTY_FEE = parseInt(process.env.PENALTY_FEE || "250", 10);
const DEFAULT_REFERRAL_PRICE = 1000;
const DEFAULT_TASK_PRICE = 500;

module.exports = {
  BOT_TOKEN,
  MONGO_URI,
  PORT,
  ADMINS,
  VIDEO_PRICE,
  PENALTY_FEE,
  DEFAULT_REFERRAL_PRICE,
  DEFAULT_TASK_PRICE,
};
