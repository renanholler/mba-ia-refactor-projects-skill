const crypto = require("crypto");

function requireAdmin(settings) {
  return (req, res, next) => {
    const header = req.get("Authorization") || "";
    const token = header.startsWith("Bearer ") ? header.slice(7) : "";
    const expected = settings.adminToken;
    const tokenBuf = Buffer.from(token);
    const expectedBuf = Buffer.from(expected);
    if (tokenBuf.length !== expectedBuf.length || !crypto.timingSafeEqual(tokenBuf, expectedBuf)) {
      res.status(401).send("Não autorizado");
      return;
    }
    next();
  };
}

module.exports = { requireAdmin };
