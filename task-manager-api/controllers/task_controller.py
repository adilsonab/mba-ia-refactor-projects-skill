from flask import jsonify, request

from controllers import serializers, validators
from services import task_service
from utils.helpers import utc_now


def list_tasks():
    now = utc_now()
    return jsonify([serializers.task_list_item(task, now) for task in task_service.list_tasks()]), 200


def get_task(task_id):
    return jsonify(serializers.task_detail(task_service.get_task(task_id))), 200


def create_task():
    fields = validators.task_create_payload(validators.json_body())
    return jsonify(task_service.create_task(fields).to_dict()), 201


def update_task(task_id):
    task_service.get_task(task_id)                       # 404 antes de validar o corpo (como no original)
    changes = validators.task_update_payload(validators.json_body())
    return jsonify(task_service.update_task(task_id, changes).to_dict()), 200


def delete_task(task_id):
    task_service.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    tasks = task_service.search_tasks(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=validators.query_int('priority'),
        user_id=validators.query_int('user_id'),
    )
    return jsonify([task.to_dict() for task in tasks]), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
