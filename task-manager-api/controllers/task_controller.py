from flask import jsonify, request

from controllers import validators
from services import task_service
from views import serializers


def list_tasks():
    return jsonify(serializers.task_list(task_service.list_tasks())), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    return jsonify(serializers.task_detail(task)), 200


def create_task():
    fields = validators.task_create_payload(validators.json_body())
    task = task_service.create_task(fields)
    return jsonify(task.to_dict()), 201


def update_task(task_id):
    task = task_service.get_task(task_id)
    changes = validators.task_update_payload(validators.json_body())
    task = task_service.update_task(task, changes)
    return jsonify(task.to_dict()), 200


def delete_task(task_id):
    task_service.delete_task(task_service.get_task(task_id))
    return jsonify({"message": "Task deletada com sucesso"}), 200


def search_tasks():
    tasks = task_service.search_tasks(
        text=request.args.get("q", ""),
        status=request.args.get("status", ""),
        priority=validators.query_int("priority", "Prioridade inválida"),
        user_id=validators.query_int("user_id", "user_id inválido"),
    )
    return jsonify(serializers.task_basic_list(tasks)), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
