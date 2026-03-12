from marshmallow import Schema, fields


class NotificationSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    actor_id = fields.Int(allow_none=True)
    event_type = fields.Str(required=True)
    title = fields.Str(required=True)
    message = fields.Str(required=True)
    resource_type = fields.Str(allow_none=True)
    resource_id = fields.Int(allow_none=True)
    is_read = fields.Bool(required=True)
    created_at = fields.DateTime(dump_only=True)
    read_at = fields.DateTime(allow_none=True)


notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)
