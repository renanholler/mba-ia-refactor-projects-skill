const userModel = require("../models/user");

async function remove(req, res, { db }) {
  try {
    await userModel.remove(db, req.params.id);
  } catch (err) {
    console.error(err);
    return res.status(500).send("Erro DB");
  }
  return res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
}

module.exports = { remove };
