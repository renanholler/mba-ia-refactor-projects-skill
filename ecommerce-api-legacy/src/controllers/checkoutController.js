const courseModel = require("../models/course");
const userModel = require("../models/user");
const enrollmentModel = require("../models/enrollment");
const paymentModel = require("../models/payment");
const auditLogModel = require("../models/auditLog");
const { chargeCard } = require("../services/paymentService");
const { hashProvidedOrRandom } = require("../security/password");

async function checkout(req, res, { db, settings, cache }) {
  const body = req.body || {};
  const name = body.usr;
  const email = body.eml;
  const password = body.pwd;
  const courseId = body.c_id;
  const cardNumber = body.card;

  if (!name || !email || !courseId || !cardNumber) {
    return res.status(400).send("Bad Request");
  }

  let course;
  try {
    course = await courseModel.findActiveById(db, courseId);
  } catch (err) {
    console.error(err);
    return res.status(404).send("Curso não encontrado");
  }
  if (!course) {
    return res.status(404).send("Curso não encontrado");
  }

  let user;
  try {
    user = await userModel.findByEmail(db, email);
  } catch (err) {
    console.error(err);
    return res.status(500).send("Erro DB");
  }

  let userId;
  if (!user) {
    try {
      userId = await userModel.create(db, name, email, hashProvidedOrRandom(password));
    } catch (err) {
      console.error(err);
      return res.status(500).send("Erro ao criar usuário");
    }
  } else {
    userId = user.id;
  }

  const status = chargeCard(cardNumber, settings.paymentGatewayKey);
  if (status === "DENIED") {
    return res.status(400).send("Pagamento recusado");
  }

  let enrollmentId;
  try {
    enrollmentId = await enrollmentModel.create(db, userId, courseId);
  } catch (err) {
    console.error(err);
    return res.status(500).send("Erro Matrícula");
  }

  try {
    await paymentModel.create(db, enrollmentId, course.price, status);
  } catch (err) {
    console.error(err);
    return res.status(500).send("Erro Pagamento");
  }

  try {
    await auditLogModel.create(db, `Checkout curso ${courseId} por ${userId}`);
  } catch (err) {
    console.error(err);
  }

  cache.save(`last_checkout_${userId}`, course.title);
  return res.status(200).json({ msg: "Sucesso", enrollment_id: enrollmentId });
}

module.exports = { checkout };
