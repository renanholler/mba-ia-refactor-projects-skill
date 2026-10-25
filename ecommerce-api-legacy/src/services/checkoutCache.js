function createCheckoutCache() {
  const store = new Map();
  return {
    save(key, data) {
      console.log(`[LOG] Salvando no cache: ${key}`);
      store.set(key, data);
    },
  };
}

module.exports = { createCheckoutCache };
