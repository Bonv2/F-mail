from flask_wtf import FlaskForm

from wtforms import PasswordField, SubmitField, BooleanField, StringField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    username = StringField('User name:', validators=[DataRequired()])
    displayname = StringField('Display name:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    password_again = PasswordField('Пароль снова:', validators=[DataRequired()])
    login_after = BooleanField('Зайти после создания:')
    submit = SubmitField('Создать')