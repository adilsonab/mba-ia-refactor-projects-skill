from flask import jsonify

from controllers import validators
from services import category_service
from views import serializers


def list_categories():
    return jsonify(serializers.category_list(category_service.list_categories_with_task_counts())), 200


def create_category():
    fields = validators.category_create_payload(validators.json_body())
    category = category_service.create_category(**fields)
    return jsonify(category.to_dict()), 201


def update_category(category_id):
    category = category_service.get_category(category_id)
    changes = validators.category_update_payload(validators.json_body(allow_empty=True))
    category = category_service.update_category(category, changes)
    return jsonify(category.to_dict()), 200


def delete_category(category_id):
    category_service.delete_category(category_service.get_category(category_id))
    return jsonify({"message": "Categoria deletada"}), 200
