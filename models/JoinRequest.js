const mongoose = require("mongoose");

const JoinRequestSchema = new mongoose.Schema({
  userId: { type: Number, required: true },
  channelId: { type: Number, required: true },
  createdAt: { type: Date, default: Date.now }
});

JoinRequestSchema.index({ userId: 1, channelId: 1 }, { unique: true });

module.exports = mongoose.model("JoinRequest", JoinRequestSchema);
