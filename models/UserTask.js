const mongoose = require("mongoose");

const UserTaskSchema = new mongoose.Schema({
  userId: { type: Number, required: true },
  taskId: { type: mongoose.Schema.Types.ObjectId, ref: "Task", required: true },
  channelId: { type: mongoose.Schema.Types.Mixed, required: true },
  reward: { type: Number, required: true },
  penalized: { type: Boolean, default: false },
  completedAt: { type: Date, default: Date.now }
});

UserTaskSchema.index({ userId: 1, taskId: 1 }, { unique: true });
UserTaskSchema.index({ completedAt: 1 });

module.exports = mongoose.model("UserTask", UserTaskSchema);
