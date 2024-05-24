from wtforms import (
    Form,
    StringField,
    TextAreaField,
    FileField,
    DateTimeLocalField,
    BooleanField,
    SubmitField,
)


class ListForm(Form):
    title = StringField(label="Title", name="list_title")
    description = TextAreaField(label="Description", name="list_description")
    image = FileField(label="Image", name="list_image")
    date = DateTimeLocalField(label="Date", name="list_date", format="%d-%m-%Y %H-%M-00")
    bringers = BooleanField(label="", name="list_bringers", default="")
    submit = SubmitField()
