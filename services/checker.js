const { Channel, User, JoinRequest } = require("../database");

async function isSubscribedToChat(telegram, chatId, userId) {
  try {
    const member = await telegram.getChatMember(chatId, userId);
    return ["creator", "administrator", "member", "restricted"].includes(member.status);
  } catch (error) {
    console.warn(`Chat a'zoligini tekshirishda xatolik (${chatId}):`, error.message);
    return false;
  }
}

async function getUnsubscribedChannels(telegram, userId) {
  const allChannels = await Channel.find();
  if (!allChannels || allChannels.length === 0) {
    return [];
  }

  const user = await User.findOne({ userId });
  const externalClicks = (user && user.subscribedExternalLinks) ? user.subscribedExternalLinks : [];

  const unsubscribed = [];

  for (const ch of allChannels) {
    const chType = ch.type;
    const chId = ch.channelId;
    const strId = ch._id.toString();

    if (chType === "public" || chType === "private") {
      if (chId) {
        const isSub = await isSubscribedToChat(telegram, chId, userId);
        if (!isSub) {
          unsubscribed.push(ch);
        }
      } else {
        unsubscribed.push(ch);
      }
    } else if (chType === "join_request") {
      // Zayavka yuborganini tekshirish
      let hasRequested = false;
      if (chId) {
        const intId = parseInt(chId, 10);
        if (!isNaN(intId)) {
          const req = await JoinRequest.findOne({ userId, channelId: intId });
          if (req) hasRequested = true;
        }

        if (!hasRequested) {
          const isSub = await isSubscribedToChat(telegram, chId, userId);
          if (!isSub) {
            unsubscribed.push(ch);
          }
        }
      } else {
        unsubscribed.push(ch);
      }
    } else if (chType === "external") {
      if (!externalClicks.includes(strId)) {
        unsubscribed.push(ch);
      }
    }
  }

  return unsubscribed;
}

module.exports = {
  isSubscribedToChat,
  getUnsubscribedChannels
};
