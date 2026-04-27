from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ComposeForm(FlaskForm):
    receiver_username = StringField(
        "Получатель",
        validators=[DataRequired()]
    )

    title = StringField(
        "Тема",
        validators=[DataRequired()]
    )

    contents = TextAreaField(
        "Сообщение"
    )

    submit = SubmitField("Отправить")