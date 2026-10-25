const reportModel = require("../models/report");

async function financialReport(req, res, { db }) {
  try {
    const report = await reportModel.financialReport(db);
    return res.json(report);
  } catch (err) {
    console.error(err);
    return res.status(500).send("Erro DB");
  }
}

module.exports = { financialReport };
