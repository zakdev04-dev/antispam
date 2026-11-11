const mongoose = require("mongoose");

const PaymentSchema = new mongoose.Schema({
  userId: { type: Number, required: true },
  amount: { type: Number, required: true },
  fileId: { type: String, required: true },
  fileType: { type: String, enum: ["photo", "document"], default: "photo" },
  status: { type: String, enum: ["pending", "approved", "rejected"], default: "pending" },
  createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model("Payment", PaymentSchema);
