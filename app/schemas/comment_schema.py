from marshmallow import Schema, fields


class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    article_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)


comment_schema = CommentSchema()
comments_schema = CommentSchema(many=True)
