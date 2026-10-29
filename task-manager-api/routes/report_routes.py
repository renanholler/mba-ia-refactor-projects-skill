from flask import Blueprint

from controllers import report_controller
from middlewares.auth import require_admin

report_bp = Blueprint("reports", __name__)


@report_bp.route("/reports/summary", methods=["GET"])
@require_admin
def summary_report():
    return report_controller.summary_report()


@report_bp.route("/reports/user/<int:user_id>", methods=["GET"])
@require_admin
def user_report(user_id):
    return report_controller.user_report(user_id)
