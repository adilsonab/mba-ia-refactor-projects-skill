from flask import jsonify

from controllers import serializers, validators
from services import category_service


def list_categories():
    rows = category_service.list_categories_with_task_count()
    return jsonify([serializers.category_with_task_count(category, count) for category, count in rows]), 200


def create_category():
    fields = validators.category_create_payload(validators.json_body())
    return jsonify(category_service.create_category(fields).to_dict()), 201


def update_category(cat_id):
    category_service.get_category(cat_id)                # 404 antes de validar o corpo (como no original)
    changes = validators.category_update_payload(validators.json_body())
    return jsonify(category_service.update_category(cat_id, changes).to_dict()), 200


def delete_category(cat_id):
    category_service.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
