from flask import g, jsonify

from controllers import serializers, validators
from middlewares.auth import ensure_self_or_admin, optional_user
from services import auth_service, user_service
from utils.errors import ForbiddenError
from utils.helpers import DEFAULT_ROLE, utc_now

ADMIN_ONLY_FIELDS = {'role', 'active'}


def list_users():
    rows = user_service.list_users_with_task_count()
    return jsonify([serializers.user_with_task_count(user, count) for user, count in rows]), 200


def get_user(user_id):
    ensure_self_or_admin(user_id)
    user = user_service.get_user(user_id)
    data = user.to_dict()
    data['tasks'] = [task.to_dict() for task in user_service.list_user_tasks(user_id)]
    return jsonify(data), 200


def create_user():
    fields = validators.user_create_payload(validators.json_body())
    caller = optional_user()
    if caller is None or not caller.is_admin():
        fields['role'] = DEFAULT_ROLE                    # cadastro público nunca escolhe o papel
    elif fields['role'] is None:
        fields['role'] = DEFAULT_ROLE
    return jsonify(user_service.create_user(**fields).to_dict()), 201


def update_user(user_id):
    ensure_self_or_admin(user_id)
    user_service.get_user(user_id)
    changes = validators.user_update_payload(validators.json_body())
    if ADMIN_ONLY_FIELDS & changes.keys() and not g.current_user.is_admin():
        raise ForbiddenError('Somente administradores alteram papel ou status')
    return jsonify(user_service.update_user(user_id, changes).to_dict()), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    ensure_self_or_admin(user_id)
    now = utc_now()
    return jsonify([serializers.user_task_item(task, now) for task in user_service.list_user_tasks(user_id)]), 200


def login():
    email, password = validators.login_payload(validators.json_body())
    user, token = auth_service.login(email, password)
    return jsonify({'message': 'Login realizado com sucesso', 'user': user.to_dict(), 'token': token}), 200
