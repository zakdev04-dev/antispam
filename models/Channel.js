const mongoose = require("mongoose");

const ChannelSchema = new mongoose.Schema({
  title: { type: String, required: true },
  type: {
    type: String,
    enum: ["public", "private", "join_request", "external"],
    required: true
  },
  channelId: { type: mongoose.Schema.Types.Mixed, default: null },
  url: { type: String, required: true },
  buttonName: { type: String, default: "< Obuna bo'lish >" },
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model("Channel", ChannelSchema);
