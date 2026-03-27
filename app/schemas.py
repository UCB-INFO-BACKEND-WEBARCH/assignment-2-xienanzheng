from marshmallow import Schema, fields, validate, EXCLUDE


class CategorySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    color = fields.Str(
        allow_none=True,
        load_default=None,
        validate=validate.Regexp(r"^#[0-9A-Fa-f]{6}$"),
    )


class TaskSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(
        allow_none=True,
        validate=validate.Length(max=500),
    )
    completed = fields.Bool()
    due_date = fields.DateTime(allow_none=True)
    category_id = fields.Int(allow_none=True)
    category = fields.Nested(CategorySchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class TaskSummarySchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(dump_only=True)
    completed = fields.Bool(dump_only=True)


class CategoryDetailSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    color = fields.Str(dump_only=True)
    tasks = fields.Nested(TaskSummarySchema, many=True, dump_only=True)


class CategoryWithCountSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
    color = fields.Str(dump_only=True)
    task_count = fields.Int(dump_only=True)
