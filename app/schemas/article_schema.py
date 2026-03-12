from marshmallow import Schema, fields


class ArticleSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    user_id = fields.Int(required=True)
    allow_comments = fields.Bool(required=True)
    is_public = fields.Bool(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
