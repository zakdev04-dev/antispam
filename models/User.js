const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
  userId: { type: Number, required: true, unique: true, index: true },
  firstName: { type: String, default: "" },
  lastName: { type: String, default: "" },
  username: { type: String, default: "" },
  phone: { type: String, default: null },
  balance: { type: Number, default: 0 },
  referrerId: { type: Number, default: null },
  referralRewarded: { type: Boolean, default: false },
  isActive: { type: Boolean, default: true },
  hasVideoAccess: { type: Boolean, default: false },
  notifiedDatabaseChannel: { type: Boolean, default: false },
  subscribedExternalLinks: [{ type: String }],
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model("User", UserSchema);
