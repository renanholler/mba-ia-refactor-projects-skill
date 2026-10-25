const express = require("express");

const { loadSettings } = require("./config/settings");
const { openDatabase, initSchema } = require("./db");
const { createCheckoutCache } = require("./services/checkoutCache");
const { registerRoutes } = require("./routes");
const { errorHandler } = require("./middlewares/errorHandler");

async function start() {
  const settings = loadSettings();
  const db = await openDatabase(settings.dbPath);
  await initSchema(db, settings);
  const cache = createCheckoutCache();

  const app = express();
  app.use(express.json());
  registerRoutes(app, { db, settings, cache });
  app.use(errorHandler);

  app.listen(settings.port, () => {
    console.log(`Frankenstein LMS rodando na porta ${settings.port}...`);
  });
}

start().catch((err) => {
  console.error(err);
  process.exit(1);
});
