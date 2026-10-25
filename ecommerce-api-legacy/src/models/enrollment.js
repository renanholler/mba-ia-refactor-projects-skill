const { run } = require("../db");

async function create(db, userId, courseId) {
  const result = await run(
    db,
    "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
    [userId, courseId]
  );
  return result.lastID;
}

module.exports = { create };
