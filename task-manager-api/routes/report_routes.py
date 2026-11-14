from flask import Blueprint

from controllers import report_controller
from middlewares.auth import admin_required, login_required

report_bp = Blueprint("reports", __name__)

report_bp.add_url_rule("/reports/summary", view_func=admin_required(report_controller.summary_report), methods=["GET"])
report_bp.add_url_rule("/reports/user/<int:user_id>", view_func=login_required(report_controller.user_report),
                       methods=["GET"])  # dono ou admin (verificado no controller)
