from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class SendForm(FlaskForm):
    to = StringField("Кому", validators=[DataRequired()])
    subject = StringField("Тема", validators=[DataRequired()])
    body = TextAreaField("Сообщение", validators=[DataRequired()])