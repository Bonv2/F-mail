import os

from flask import Flask, render_template, redirect, flash, request, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

from data import users_resource, emails_resource
from data import db_session
from data.users import User
from data.emails import Email

from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.compose_form import ComposeForm


app = Flask(__name__)
api = Api(app)

# ---------------- API ---------------- #

api.add_resource(users_resource.UsersListResource, '/api/users')
api.add_resource(users_resource.UserLoginResource, '/api/login')
api.add_resource(users_resource.UserThisOneResource, '/api/this_user')
api.add_resource(users_resource.UsersResource, '/api/users/<string:username>')

api.add_resource(emails_resource.EmailsListResource, '/api/emails')
api.add_resource(emails_resource.EmailsResource, '/api/emails/<int:id>')

# ---------------- CONFIG ---------------- #

SECRET_KEY = os.environ.get("SECRET_KEY") or "DELETE_ME_PLEASE_DONT_RELEASE"
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set")

app.config["SECRET_KEY"] = SECRET_KEY

# ---------------- LOGIN MANAGER ---------------- #

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


# ---------------- PFP ---------------- #

@app.route("/pfp/<path:filename>")
def user_pfp(filename):
    return send_from_directory("db/pfps", filename)

# ---------------- WEB ROUTES ---------------- #

@app.route("/")
@app.route("/index")
def index():
    if current_user.is_authenticated:
        return redirect("/mailbox")
    return render_template("welcome.html", title="Fig-mail")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect("/mailbox")

    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.get(User, form.username.data)

        if not user or not user.check_password(form.password.data):
            flash("Неверный логин или пароль")
            return render_template("login.html", title="Вход", form=form)

        login_user(user, remember=form.remember_me.data)
        return redirect("/mailbox")

    return render_template("login.html", title="Вход", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect("/mailbox")

    form = RegisterForm()

    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash("Пароли не совпадают")
            return render_template(
                "register.html",
                title="Регистрация",
                form=form
            )

        db_sess = db_session.create_session()

        if db_sess.get(User, form.username.data):
            flash("Такой username уже существует")
            return render_template(
                "register.html",
                title="Регистрация",
                form=form
            )

        user = User(
            username=form.username.data,
            displayname=form.displayname.data
        )
        user.set_password(form.password.data)

        if form.pfp.data:
            import os

            filename = f"{form.username.data}.jpg"
            save_path = os.path.join("db", "pfps", filename)

            form.pfp.data.save(save_path)
            user.pfp = filename

        db_sess.add(user)
        db_sess.commit()

        if form.login_after.data:
            login_user(user)
            return redirect("/mailbox")

        flash("Аккаунт успешно создан")
        return redirect("/login")

    return render_template("register.html", title="Регистрация", form=form)


@app.route("/mailbox")
@login_required
def mailbox():
    db_sess = db_session.create_session()
    mail_type = request.args.get("type", "inbox")

    if mail_type == "outbox":
        emails = db_sess.query(Email).filter(
            Email.sender_username == current_user.username
        ).all()
    else:
        mail_type = "inbox"
        emails = db_sess.query(Email).filter(
            Email.receiver_username == current_user.username
        ).all()

    return render_template(
        "mailbox.html",
        title="Почта",
        emails=emails,
        mail_type=mail_type
    )


@app.route("/email/<int:email_id>")
@login_required
def email_view(email_id):
    db_sess = db_session.create_session()
    email = db_sess.get(Email, email_id)

    if not email:
        flash("Письмо не найдено")
        return redirect("/mailbox")

    if (
        email.sender_username != current_user.username
        and email.receiver_username != current_user.username
        and current_user.username != "admin"
    ):
        flash("Нет доступа")
        return redirect("/mailbox")

    return render_template(
        "email_view.html",
        title=email.title,
        email=email
    )


@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    form = ComposeForm()

    receiver = request.args.get("receiver")
    title = request.args.get("title")

    if receiver and request.method == "GET":
        form.receiver_username.data = receiver

    if title and request.method == "GET":
        form.title.data = f"RE: {title}"

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        target_user = db_sess.get(User, form.receiver_username.data)
        sender_user = db_sess.get(User, current_user.username)

        if not target_user:
            flash("Получатель не найден")
            return render_template("compose.html", title="Новое письмо", form=form)

        if target_user.username == sender_user.username:
            flash("Нельзя отправить письмо самому себе")
            return render_template("compose.html", title="Новое письмо", form=form)

        email = Email(
            sender=sender_user,
            receiver=target_user,
            title=form.title.data,
            contents=form.contents.data
        )

        db_sess.add(email)
        db_sess.commit()

        flash("Письмо отправлено")
        return redirect("/mailbox")

    return render_template("compose.html", title="Новое письмо", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == "__main__":
    main()