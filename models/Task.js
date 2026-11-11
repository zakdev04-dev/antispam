const mongoose = require("mongoose");

const TaskSchema = new mongoose.Schema({
  title: { type: String, required: true },
  taskType: {
    type: String,
    enum: ["channel", "group", "join_request"],
    required: true
  },
  channelId: { type: mongoose.Schema.Types.Mixed, required: true },
  url: { type: String, required: true },
  reward: { type: Number, required: true, default: 500 },
  isActive: { type: Boolean, default: true },
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model("Task", TaskSchema);
