from marshmallow import Schema, fields, validate


class List:
    def __init__(
        self,
        creator_id,
        title,
        description,
        list_url,
        list_thumb_url,
        list_medium_url,
        delete_list_url,
        created_at,
        updated_at,
        expires_at,
    ):
        self.creator_id = creator_id
        self.title = title
        self.description = description
        self.list_url = list_url
        self.list_thumb_url = list_thumb_url
        self.list_medium_url = list_medium_url
        self.delete_list_url = delete_list_url
        self.created_at = created_at
        self.updated_at = updated_at
        self.expires_at = expires_at


class ListSchema(Schema):
    creator_id = fields.Int(required=True, validate=validate.Range(min=1))
    title = fields.Str(
        required=True,
        validate=validate.Regexp("^[a-zA-Z0-9'-_#$=@:\/;\.\?\,\!]{,50}$"),
    )
    description = fields.Str(
        required=False,
        validate=validate.Regexp("^[a-zA-Z0-9'-_#$=@:\/;\.\?\,\!]{,200}$"),
        allow_none=True,
    )
    list_url = fields.Url(required=False, allow_none=True)
    list_thumb_url = fields.Url(required=False, allow_none=True)
    list_medium_url = fields.Url(required=False, allow_none=True)
    delete_list_url = fields.Url(required=False, allow_none=True)
    created_at = fields.DateTime(required=False)
    updated_at = fields.DateTime(required=False)
    expires_at = fields.DateTime(required=True)
