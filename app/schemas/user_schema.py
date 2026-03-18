from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    fullname = fields.Str(required=True)
    email = fields.Email(required=True)
    avatar_url = fields.Str(dump_only=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)
