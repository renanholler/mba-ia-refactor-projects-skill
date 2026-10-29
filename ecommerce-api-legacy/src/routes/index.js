const { checkout } = require("../controllers/checkoutController");
const { financialReport } = require("../controllers/reportController");
const { remove } = require("../controllers/userController");
const { requireAdmin } = require("../middlewares/requireAdmin");

function forward(handler, deps) {
  return (req, res, next) => {
    Promise.resolve(handler(req, res, deps)).catch(next);
  };
}

function registerRoutes(app, deps) {
  const admin = requireAdmin(deps.settings);
  app.post("/api/checkout", forward(checkout, deps));
  app.get("/api/admin/financial-report", admin, forward(financialReport, deps));
  app.delete("/api/users/:id", admin, forward(remove, deps));
}

module.exports = { registerRoutes };
