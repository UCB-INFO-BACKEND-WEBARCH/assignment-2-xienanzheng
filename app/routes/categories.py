from flask import Blueprint
from marshmallow import ValidationError
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Category, Task
from ..schemas import CategoryDetailSchema, CategorySchema


categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


category_schema = CategorySchema()
category_detail_schema = CategoryDetailSchema()


@categories_bp.get("")
def list_categories():
    rows = (
        db.session.query(Category, func.count(Task.id).label("task_count"))
        .outerjoin(Task)
        .group_by(Category.id)
        .order_by(Category.id)
        .all()
    )

    categories = []
    for category, task_count in rows:
        categories.append(
            {
                "id": category.id,
                "name": category.name,
                "color": category.color,
                "task_count": int(task_count),
            }
        )

    return {"categories": categories}, 200


@categories_bp.get("/<int:category_id>")
def get_category(category_id):
    category = (
        Category.query.options(selectinload(Category.tasks))
        .filter(Category.id == category_id)
        .first()
    )
    if not category:
        return {"error": "Category not found"}, 404

    return category_detail_schema.dump(category), 200


@categories_bp.post("")
def create_category():
    payload = request.get_json(silent=True) or {}

    try:
        data = category_schema.load(payload)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    existing = Category.query.filter(Category.name == data["name"]).first()
    if existing:
        return {"errors": {"name": ["Category with this name already exists."]}}, 400

    category = Category(**data)
    db.session.add(category)
    db.session.commit()

    return {"category": category_schema.dump(category)}, 201


@categories_bp.delete("/<int:category_id>")
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return {"error": "Category not found"}, 404

    if category.tasks:
        return {
            "error": "Cannot delete category with existing tasks. Move or delete tasks first."
        }, 400

    db.session.delete(category)
    db.session.commit()

    return {"message": "Category deleted"}, 200
