from marshmallow import Schema, fields


class MessageSchema(Schema):
    id = fields.Int(dump_only=True)
    sender_id = fields.Int(required=True)
    receiver_id = fields.Int(required=True)
    content = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)
