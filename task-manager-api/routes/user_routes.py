"""Rotas de usuários e login.

Matriz de acesso:
  público          POST /login, POST /users (papel sempre 'user', salvo token de admin)
  dono ou admin    GET/PUT /users/<id>, GET /users/<id>/tasks (role/active só admin)
  admin            GET /users, DELETE /users/<id>
"""
from flask import Blueprint

from controllers import user_controller as ctrl
from middlewares.auth import admin_required, login_required

user_bp = Blueprint('users', __name__)

user_bp.add_url_rule('/users', view_func=admin_required(ctrl.list_users), methods=['GET'])
user_bp.add_url_rule('/users', view_func=ctrl.create_user, methods=['POST'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=login_required(ctrl.get_user), methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=login_required(ctrl.update_user), methods=['PUT'])
user_bp.add_url_rule('/users/<int:user_id>', view_func=admin_required(ctrl.delete_user), methods=['DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/tasks', view_func=login_required(ctrl.get_user_tasks), methods=['GET'])
user_bp.add_url_rule('/login', view_func=ctrl.login, methods=['POST'])
