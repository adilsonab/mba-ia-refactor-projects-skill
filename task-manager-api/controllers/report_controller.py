from flask import jsonify

from middlewares.auth import ensure_self_or_admin
from services import report_service, user_service


def summary_report():
    return jsonify(report_service.summary_report()), 200


def user_report(user_id):
    ensure_self_or_admin(user_id)
    user = user_service.get_user(user_id)
    return jsonify(report_service.user_report(user)), 200
