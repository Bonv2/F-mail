import os

from flask import Flask
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_restful import Api

from data import users_resource
from data import db_session

app = Flask(__name__)
api = Api(app)
api.add_resource(users_resource.UsersListResource, '/api/users')
api.add_resource(users_resource.UsersResource, '/api/users/<string:username>')

if not os.environ.get("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY not set")

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')


def main():
    db_session.global_init("db/users.db")
    app.run()


if __name__ == '__main__':
    main()