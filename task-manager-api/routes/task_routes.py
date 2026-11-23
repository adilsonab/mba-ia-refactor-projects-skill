"""Rotas de tasks — acesso: usuário autenticado (sistema fechado)."""
from flask import Blueprint

from controllers import task_controller as ctrl
from middlewares.auth import login_required

task_bp = Blueprint('tasks', __name__)

task_bp.add_url_rule('/tasks', view_func=login_required(ctrl.list_tasks), methods=['GET'])
task_bp.add_url_rule('/tasks', view_func=login_required(ctrl.create_task), methods=['POST'])
task_bp.add_url_rule('/tasks/search', view_func=login_required(ctrl.search_tasks), methods=['GET'])
task_bp.add_url_rule('/tasks/stats', view_func=login_required(ctrl.task_stats), methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=login_required(ctrl.get_task), methods=['GET'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=login_required(ctrl.update_task), methods=['PUT'])
task_bp.add_url_rule('/tasks/<int:task_id>', view_func=login_required(ctrl.delete_task), methods=['DELETE'])
