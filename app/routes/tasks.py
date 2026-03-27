from datetime import datetime, timezone

from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..jobs import get_queue, send_due_date_notification, should_queue_notification
from ..models import Category, Task
from ..schemas import TaskSchema


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


task_schema = TaskSchema()
task_schema_no_category = TaskSchema(exclude=("category",))
task_list_schema = TaskSchema(many=True)


def parse_completed(value):
    if value is None:
        return None
    lowered = value.strip().lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    return "invalid"


@tasks_bp.get("")
def list_tasks():
    completed_param = request.args.get("completed")
    completed = parse_completed(completed_param)
    if completed == "invalid":
        return {"error": "Invalid completed filter. Use true or false."}, 400

    query = Task.query.options(joinedload(Task.category)).order_by(Task.id)
    if completed is not None:
        query = query.filter(Task.completed.is_(completed))

    tasks = query.all()
    return {"tasks": task_list_schema.dump(tasks)}, 200


@tasks_bp.get("/<int:task_id>")
def get_task(task_id):
    task = (
        Task.query.options(joinedload(Task.category))
        .filter(Task.id == task_id)
        .first()
    )
    if not task:
        return {"error": "Task not found"}, 404

    return {"task": task_schema.dump(task)}, 200


@tasks_bp.post("")
def create_task():
    payload = request.get_json(silent=True) or {}

    try:
        data = task_schema.load(payload)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    category_id = data.get("category_id")
    if category_id is not None:
        category = db.session.get(Category, category_id)
        if not category:
            return {"errors": {"category_id": ["Category not found."]}}, 400

    task = Task(**data)
    db.session.add(task)
    db.session.commit()

    notification_queued = False
    if should_queue_notification(task.due_date, datetime.now(timezone.utc)):
        queue = get_queue()
        queue.enqueue(send_due_date_notification, task.title)
        notification_queued = True

    return {
        "task": task_schema_no_category.dump(task),
        "notification_queued": notification_queued,
    }, 201


@tasks_bp.put("/<int:task_id>")
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {"error": "Task not found"}, 404

    payload = request.get_json(silent=True) or {}
    try:
        data = task_schema.load(payload, partial=True)
    except ValidationError as err:
        return {"errors": err.messages}, 400

    if "category_id" in data:
        category_id = data.get("category_id")
        if category_id is not None:
            category = db.session.get(Category, category_id)
            if not category:
                return {"errors": {"category_id": ["Category not found."]}}, 400

    for key, value in data.items():
        setattr(task, key, value)

    db.session.commit()

    return {"task": task_schema_no_category.dump(task)}, 200


@tasks_bp.delete("/<int:task_id>")
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {"error": "Task not found"}, 404

    db.session.delete(task)
    db.session.commit()

    return {"message": "Task deleted"}, 200
