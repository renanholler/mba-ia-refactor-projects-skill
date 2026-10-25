const { checkout } = require("../controllers/checkoutController");
const { financialReport } = require("../controllers/reportController");
const { remove } = require("../controllers/userController");

function forward(handler, deps) {
  return (req, res, next) => {
    Promise.resolve(handler(req, res, deps)).catch(next);
  };
}

function registerRoutes(app, deps) {
  // A API não tem sessão. Relatório financeiro e exclusão de usuário seguem sem checagem de identidade.
  app.post("/api/checkout", forward(checkout, deps));
  app.get("/api/admin/financial-report", forward(financialReport, deps));
  app.delete("/api/users/:id", forward(remove, deps));
}

module.exports = { registerRoutes };
