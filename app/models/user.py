from marshmallow import Schema, fields, validate


class User:
    def __init__(self, email, password, confirmation):
        self.email = email
        self.password = password
        self.confirmation = confirmation


class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Regexp("[a-zA-Z0-9]{8,}"))
    confirmation = fields.Str(
        required=True, validate=validate.Regexp("[a-zA-Z0-9]{8,}")
    )
