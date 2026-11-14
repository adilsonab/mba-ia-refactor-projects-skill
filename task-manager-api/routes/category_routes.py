from flask import Blueprint

from controllers import category_controller
from middlewares.auth import admin_required, login_required

category_bp = Blueprint("categories", __name__)

category_bp.add_url_rule("/categories", view_func=login_required(category_controller.list_categories), methods=["GET"])
category_bp.add_url_rule("/categories", view_func=admin_required(category_controller.create_category), methods=["POST"])
category_bp.add_url_rule("/categories/<int:category_id>", view_func=admin_required(category_controller.update_category),
                         methods=["PUT"])
category_bp.add_url_rule("/categories/<int:category_id>", view_func=admin_required(category_controller.delete_category),
                         methods=["DELETE"])
