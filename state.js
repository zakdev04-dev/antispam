const states = new Map();

function getState(userId) {
  return states.get(userId) || null;
}

function setState(userId, stateName, data = {}) {
  states.set(userId, { state: stateName, data });
}

function updateData(userId, newData = {}) {
  const current = states.get(userId) || { state: null, data: {} };
  states.set(userId, {
    state: current.state,
    data: { ...current.data, ...newData }
  });
}

function clearState(userId) {
  states.delete(userId);
}

module.exports = {
  getState,
  setState,
  updateData,
  clearState
};
