const crypto = require("crypto");

const PBKDF2_ITERATIONS = 260000;
const PBKDF2_KEYLEN = 32;
const PBKDF2_DIGEST = "sha256";

function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const digest = crypto
    .pbkdf2Sync(String(password), salt, PBKDF2_ITERATIONS, PBKDF2_KEYLEN, PBKDF2_DIGEST)
    .toString("hex");
  return `pbkdf2$${PBKDF2_ITERATIONS}$${salt}$${digest}`;
}

function hashProvidedOrRandom(password) {
  if (password) return hashPassword(password);
  return hashPassword(crypto.randomBytes(16).toString("hex"));
}

module.exports = { hashPassword, hashProvidedOrRandom };
