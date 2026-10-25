function errorHandler(err, req, res, next) {
  console.error(err);
  if (res.headersSent) {
    next(err);
    return;
  }
  res.status(500).send("Erro interno");
}

module.exports = { errorHandler };
