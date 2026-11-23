"""Rotas de categorias — leitura: autenticado; escrita: admin."""
from flask import Blueprint

from controllers import category_controller as ctrl
from middlewares.auth import admin_required, login_required

category_bp = Blueprint('categories', __name__)

category_bp.add_url_rule('/categories', view_func=login_required(ctrl.list_categories), methods=['GET'])
category_bp.add_url_rule('/categories', view_func=admin_required(ctrl.create_category), methods=['POST'])
category_bp.add_url_rule('/categories/<int:cat_id>', view_func=admin_required(ctrl.update_category), methods=['PUT'])
category_bp.add_url_rule('/categories/<int:cat_id>', view_func=admin_required(ctrl.delete_category),
                         methods=['DELETE'])
