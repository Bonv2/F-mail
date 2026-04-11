from flask_restful import reqparse, abort, Resource
from flask import jsonify

from . import db_session
from .users import User

def abort_if_user_not_found(username):
    session = db_session.create_session()
    user = session.query(User).get(username)
    if not user:
        abort(404, message=f"User {username} not found")


class UsersResource(Resource):
    def get(self, username):
        abort_if_user_not_found(username)
        session = db_session.create_session()
        user = session.get(User, username)
        user_dict = user.to_dict(only=('username', 'displayname'))
        try:
            with open(user.pfp, "rb") as f:
                pfp = f.read()
            user_dict["pfp"] = pfp
        except Exception as e:
            pass
        return jsonify({
            'users': [user_dict]
        })


    def put(self, username):
        abort_if_user_not_found(username)
        ...


    def delete(self, username):
        abort_if_user_not_found(username)

        session = db_session.create_session()
        user = session.get(User, username)
        ...


class UsersListResource(Resource):
    def get(self):
        ...

    def post(self):
        ...