import os

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

from data import users_resource, emails_resource
from data import db_session
from data.users import User

app = Flask(__name__)
api = Api(app)
api.add_resource(users_resource.UsersListResource, '/api/users')
api.add_resource(users_resource.UserLoginResource, '/api/login')
api.add_resource(users_resource.UserThisOneResource, '/api/this_user')
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
    return render_template("base_temp.html")


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()