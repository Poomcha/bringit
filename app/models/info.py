from marshmallow import Schema, fields, validate


class Info:
    def __init__(
        self,
        user_id,
        firstname,
        lastname,
        username,
        description,
        avatar_url,
        avatar_thumb_url,
        avatar_medium_url,
        delete_avatar_url,
    ):
        self.user_id = user_id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.description = description
        self.avatar_url = avatar_url
        self.avatar_thumb_url = avatar_thumb_url
        self.avatar_medium_url = avatar_medium_url
        self.delete_avatar_url = delete_avatar_url


class InfoSchema(Schema):
    user_id = fields.Int(required=False, validate=validate.Range(min=1))
    firstname = fields.Str(required=True, validate=validate.Regexp("^[a-zA-Z]{1,20}$"))
    lastname = fields.Str(required=True, validate=validate.Regexp("^[a-zA-Z]{1,20}$"))
    username = fields.Str(
        required=False,
        validate=validate.Regexp("^[a-zA-Z]{1,20}\.[a-zA-Z]{1,20}#\d{1,4}$"),
    )
    description = fields.Str(
        required=False,
        validate=validate.Regexp("^[a-zA-Z0-9'\-_#$=@:\/;\.\?\,\!\s]{0,200}$"),
        allow_none=True,
    )
    avatar_url = fields.Url(required=False, allow_none=True)
    avatar_thumb_url = fields.Url(required=False, allow_none=True)
    avatar_medium_url = fields.Url(required=False, allow_none=True)
    delete_avatar_url = fields.Url(required=False, allow_none=True)
