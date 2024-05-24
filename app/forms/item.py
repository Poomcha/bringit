from wtforms import (
    Form,
    StringField,
    TextAreaField,
    FileField,
    DateField,
    URLField,
    FormField,
)

from wtforms.widgets import ListWidget


class ItemForm(Form):
    title = StringField(label="Title", name="item_title")
    description = TextAreaField(label="Description", name="item_description")
    image = FileField(label="Image", name="item_image")
    external_link = URLField(label="URL", name="item_url")
    type = StringField(label="Type", name="item_type")


class ItemFormList(Form):
    itemform = FormField(ItemForm, label="", widget=ListWidget())

