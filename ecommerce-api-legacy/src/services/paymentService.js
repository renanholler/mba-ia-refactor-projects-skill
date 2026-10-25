const PAID_CARD_PREFIX = "4";

function chargeCard(cardNumber, gatewayKey) {
  if (typeof gatewayKey !== "string" || gatewayKey.length === 0) {
    throw new Error("PAYMENT_GATEWAY_KEY ausente");
  }
  return String(cardNumber).startsWith(PAID_CARD_PREFIX) ? "PAID" : "DENIED";
}

module.exports = { chargeCard, PAID_CARD_PREFIX };
