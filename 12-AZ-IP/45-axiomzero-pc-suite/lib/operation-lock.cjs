function createExclusiveOperation(message) {
  let active = false;
  return async function run(operation) {
    if (active) throw new Error(message);
    active = true;
    try {
      return await operation();
    } finally {
      active = false;
    }
  };
}

module.exports = { createExclusiveOperation };
