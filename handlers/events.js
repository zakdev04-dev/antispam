const { JoinRequest, User } = require("../database");

async function handleChatJoinRequest(ctx) {
  try {
    const update = ctx.update.chat_join_request;
    if (!update) return;

    const userId = update.from.id;
    const channelId = update.chat.id;

    await JoinRequest.findOneAndUpdate(
      { userId, channelId },
      { userId, channelId, createdAt: new Date() },
      { upsert: true }
    );
    console.log(`Yangi zayavka saqlandi: userId=${userId}, channelId=${channelId}`);
  } catch (err) {
    console.error("Zayavkani saqlashda xatolik:", err.message);
  }
}

async function handleMyChatMember(ctx) {
  try {
    const update = ctx.update.my_chat_member;
    if (!update) return;

    const userId = update.from.id;
    const newStatus = update.new_chat_member.status;

    if (["kicked", "left"].includes(newStatus)) {
      await User.updateOne({ userId }, { isActive: false });
      console.log(`Foydalanuvchi botni blokladi/to'xtatdi: ${userId}`);
    } else if (newStatus === "member") {
      await User.updateOne({ userId }, { isActive: true });
      console.log(`Foydalanuvchi botni qayta faollashtirdi: ${userId}`);
    }
  } catch (err) {
    console.error("handleMyChatMember xatoligi:", err.message);
  }
}

module.exports = {
  handleChatJoinRequest,
  handleMyChatMember
};
