from marshmallow import Schema, fields


class LikeSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    article_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)


like_schema = LikeSchema()
likes_schema = LikeSchema(many=True)
