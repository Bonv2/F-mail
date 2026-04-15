from flask_wtf import FlaskForm

from wtforms import EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = EmailField('User name:', validators=[DataRequired()])
    password = PasswordField('Пароль:', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня:')
    submit = SubmitField('Войти')