from marshmallow import Schema, fields, validate


class Item:
    def __init__(self):
        self.creator_id = creator_id
        self.title = title
        self.description = description
        self.exernal_link = external_link
        self.type = type
        self.item_url = list_url
        self.item_thumb_url = list_thumb_url
        self.item_medium_url = list_medium_url
        self.delete_item_url = delete_item_url
        self.created_at = created_at
        self.updated_at = updated_at
        self.expires_at = expires_at


class ItemSchema(Schema):
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
    external_link = fields.Url(required=False, allow_none=True)
    type = fields.Str(
        required=False,
        validate=validate.Regexp("^[a-zA-Z0-9'-_#$=@:\/;\.\?\,\!]{,20}$"),
        allow_none=True,
    )
    item_url = fields.Url(required=False, allow_none=True)
    item_thumb_url = fields.Url(required=False, allow_none=True)
    item_medium_url = fields.Url(required=False, allow_none=True)
    delete_item_url = fields.Url(required=False, allow_none=True)
    created_at = fields.DateTime(required=False)
    updated_at = fields.DateTime(required=False)
    expires_at = fields.DateTime(required=False)
