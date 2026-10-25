const { run } = require("../db");

function create(db, enrollmentId, amount, status) {
  return run(
    db,
    "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
    [enrollmentId, amount, status]
  );
}

module.exports = { create };
