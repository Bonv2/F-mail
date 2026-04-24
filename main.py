import os

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

from data import users_resource, emails_resource
from data import db_session
from data.users import User

from data.emails import Email

app = Flask(__name__)
api = Api(app)
api.add_resource(users_resource.UsersListResource, '/api/users')
api.add_resource(users_resource.UserLoginResource, '/api/login')
api.add_resource(users_resource.UsersResource, '/api/users/<string:username>')

api.add_resource(emails_resource.EmailsListResource, '/api/emails')
api.add_resource(emails_resource.EmailsResource, '/api/emails/<int:id>')

SECRET_KEY = os.environ.get('SECRET_KEY') or "DELETE_ME_PLEASE_DONT_RELEASE" # fixme: DELETE

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set")

app.config['SECRET_KEY'] = SECRET_KEY


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect("/inbox")
    return redirect("/login")

from forms.send_form import SendForm

from data.emails_resource import send_email

@app.route('/send', methods=['GET', 'POST'])
@login_required
def send():
    form = SendForm()

    if form.validate_on_submit():
        try:
            send_email({
                "receiver_username": form.to.data,
                "title": form.subject.data,
                "contents": form.body.data
            })
            return redirect('/inbox')

        except Exception as e:
            return render_template('send.html', form=form, message=str(e))

    return render_template('send.html', form=form)

@app.route('/inbox')
@login_required
def inbox():
    data = get_emails()
    return render_template("inbox.html", mails=data['emails'])

@app.route('/mail/<int:id>')
@login_required
def mail(id):
    db_sess = db_session.create_session()

    mail = db_sess.get(Email, id)

    # защита (очень важно)
    if mail.receiver_username != current_user.username and mail.sender_username != current_user.username:
        return "Нет доступа", 403

    return render_template("mail.html", mail=mail)

@app.route('/sent')
@login_required
def sent():
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.username)

    return render_template("sent.html", mails=user.outbox)

from forms.register_form import RegisterForm
from flask import flash

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()

        if db_sess.get(User, form.username.data):
            return render_template('register.html', form=form, message="Пользователь уже есть")

        user = User(
            username=form.username.data,
            displayname=form.displayname.data
        )
        user.set_password(form.password.data)

        db_sess.add(user)
        db_sess.commit()

        if form.login_after.data:
            login_user(user)
            return redirect('/inbox')

        return redirect('/login')

    return render_template('register.html', form=form)

from forms.login_form import LoginForm

import requests

from data.users_resource import login_user_api

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            login_user_api(form.username.data, form.password.data)
            return redirect('/inbox')
        except Exception:
            return render_template('login.html', form=form, message="Неверный логин или пароль")

    return render_template('login.html', form=form)


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()