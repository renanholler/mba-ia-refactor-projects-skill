const { get, run } = require("../db");

function findByEmail(db, email) {
  return get(db, "SELECT id FROM users WHERE email = ?", [email]);
}

async function create(db, name, email, passwordHash) {
  const result = await run(db, "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [
    name,
    email,
    passwordHash,
  ]);
  return result.lastID;
}

function remove(db, id) {
  return run(db, "DELETE FROM users WHERE id = ?", [id]);
}

module.exports = { findByEmail, create, remove };
