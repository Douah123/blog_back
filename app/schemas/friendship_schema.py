from marshmallow import Schema, fields


class FriendshipSchema(Schema):
    id = fields.Int(dump_only=True)
    requester_id = fields.Int(required=True)
    addressee_id = fields.Int(required=True)
    status = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)


friendship_schema = FriendshipSchema()
friendships_schema = FriendshipSchema(many=True)
