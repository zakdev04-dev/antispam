const { UserTask, User } = require("../database");
const config = require("../config");

async function checkPenalties(telegram) {
  console.log("30 kunlik vazifa jarimalarini tekshirish boshlandi...");
  try {
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
    const recentTasks = await UserTask.find({
      completedAt: { $gte: thirtyDaysAgo },
      penalized: false
    });

    for (const rec of recentTasks) {
      const { userId, channelId, reward, _id } = rec;
      if (!channelId) continue;

      try {
        const member = await telegram.getChatMember(channelId, userId);
        if (["left", "kicked"].includes(member.status)) {
          const penalty = reward + config.PENALTY_FEE;
          await User.updateOne({ userId }, { $inc: { balance: -penalty } });
          rec.penalized = true;
          await rec.save();

          try {
            await telegram.sendMessage(
              userId,
              `⚠️ <b>Jarima qo'llandi!</b>\n\n` +
              `Siz 30 kun ichida vazifa kanalidan/guruhidan chiqib ketganingiz aniqlandi.\n` +
              `Balansingizdan vazifa narxi (${reward.toLocaleString()} UZS) + 250 UZS jarima ` +
              `(jami <b>-${penalty.toLocaleString()} UZS</b>) yechib olindi!\n\n` +
              `<i>Iltimos, vazifa shartlariga qat'iy rioya qiling!</i>`,
              { parse_mode: "HTML" }
            );
          } catch (err) {
            if (err.response && err.response.error_code === 403) {
              await User.updateOne({ userId }, { isActive: false });
            }
          }
        }
      } catch (err) {
        console.warn(`Jarima tekshiruvida xatolik (${channelId}):`, err.message);
      }
    }
  } catch (err) {
    console.error("checkPenalties umumiy xatoligi:", err);
  }
}

module.exports = {
  checkPenalties
};
