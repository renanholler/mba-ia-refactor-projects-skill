const { all } = require("../db");

const REPORT_SQL = `
  SELECT
    c.id AS course_id,
    c.title AS course,
    e.id AS enrollment_id,
    u.name AS student_name,
    pay.amount AS amount,
    pay.status AS payment_status
  FROM courses c
  LEFT JOIN enrollments e ON e.course_id = c.id
  LEFT JOIN users u ON u.id = e.user_id
  LEFT JOIN payments pay ON pay.id = (
    SELECT p.id FROM payments p WHERE p.enrollment_id = e.id ORDER BY p.id LIMIT 1
  )
  ORDER BY c.id, e.id
`;

async function financialReport(db) {
  const rows = await all(db, REPORT_SQL);
  return groupReport(rows);
}

function groupReport(rows) {
  const courses = [];
  const index = new Map();

  for (const row of rows) {
    if (!index.has(row.course_id)) {
      const item = { course: row.course, revenue: 0, students: [] };
      index.set(row.course_id, item);
      courses.push(item);
    }
    if (row.enrollment_id == null) continue;

    const item = index.get(row.course_id);
    const paid = row.amount == null ? 0 : row.amount;
    if (row.payment_status === "PAID") {
      item.revenue += paid;
    }
    item.students.push({
      student: row.student_name == null ? "Unknown" : row.student_name,
      paid,
    });
  }

  return courses;
}

module.exports = { financialReport };
