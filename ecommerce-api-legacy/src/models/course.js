const { get } = require("../db");

function findActiveById(db, id) {
  return get(db, "SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
}

module.exports = { findActiveById };
