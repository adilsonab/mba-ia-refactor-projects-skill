from flask import jsonify

from controllers import validators
from services import user_service
from views import serializers


def list_users():
    return jsonify(serializers.user_list(user_service.list_users_with_task_counts())), 200


def get_user(user_id):
    user = user_service.get_user(user_id)
    return jsonify(serializers.user_detail(user, user_service.get_user_tasks(user))), 200


def create_user():
    fields = validators.user_create_payload(validators.json_body())
    user = user_service.create_user(**fields)
    return jsonify(user.to_dict()), 201


def update_user(user_id):
    user = user_service.get_user(user_id)
    changes = validators.user_update_payload(validators.json_body())
    user = user_service.update_user(user, changes)
    return jsonify(user.to_dict()), 200


def delete_user(user_id):
    user_service.delete_user(user_service.get_user(user_id))
    return jsonify({"message": "Usuário deletado com sucesso"}), 200


def get_user_tasks(user_id):
    user = user_service.get_user(user_id)
    return jsonify(serializers.user_task_list(user_service.get_user_tasks(user))), 200


def login():
    email, password = validators.login_payload(validators.json_body())
    user = user_service.authenticate(email, password)
    return jsonify(serializers.login_response(user, user_service.issue_token(user))), 200
