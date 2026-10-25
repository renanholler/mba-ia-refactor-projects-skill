function loadSettings() {
  return {
    port: Number(process.env.PORT || 3000),
    dbPath: process.env.DATABASE_PATH || ":memory:",
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "dev-only-change-me",
    seedUserPassword: process.env.SEED_USER_PASSWORD || null,
  };
}

module.exports = { loadSettings };
