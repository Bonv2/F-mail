from flask_login import current_user, login_user, login_required
from flask_restful import reqparse, abort, Resource
from flask import jsonify, make_response
from PIL import Image
import base64
import os
from io import BytesIO

from . import db_session
from .users import User

add_user_parser = reqparse.RequestParser()
add_user_parser.add_argument("username", required=True)
add_user_parser.add_argument("displayname", required=True)
add_user_parser.add_argument("password", required=True)
add_user_parser.add_argument("pfp", required=False, type=str)

edit_user_parser = reqparse.RequestParser()
edit_user_parser.add_argument("displayname", required=False)
edit_user_parser.add_argument("pfp", required=False, type=str)

login_user_parser = reqparse.RequestParser()
login_user_parser.add_argument("password", required=True)
login_user_parser.add_argument("username", required=True)


def login_user_api(username, password):
    db_sess = db_session.create_session()
    user = db_sess.get(User, username)
    if not user:
        raise Exception(f"Incorrect username or password")
    if user.check_password(password):
        login_user(user)
        return {"message": "success, check cookies"}
    raise Exception(f"Incorrect username or password")


def get_one_user(username):
    abort_if_user_not_found(username)
    session = db_session.create_session()
    user = session.get(User, username)
    user_dict = user.to_dict(only=('username', 'displayname'))
    try:
        with open(f"db/pfps/{user.pfp}", "rb") as f:
            pfp = f.read()
        user_dict["pfp"] = base64.b64encode(pfp).decode()
    except Exception as e:
        pass
    return {'users': [user_dict]}


def edit_user(username, args: dict):
    abort_if_user_not_found(username)
    db_sess = db_session.create_session()

    cur_user = current_user
    target_user = db_sess.get(User, username)
    if cur_user != target_user and cur_user.username != "admin":
        raise PermissionError(f"No permission to edit {target_user.username}. as {cur_user.username}, you can only edit yourself")
    if args["displayname"]:
        target_user.displayname = args["displayname"]
    if args["pfp"]:
        pfp_path = f"db/pfps/{target_user.username}"
        if os.path.exists(pfp_path):
            os.remove(f"db/pfps/{target_user.username}.jpg")
        img_data = args['pfp'].encode()
        img = Image.open(BytesIO(base64.b64decode(img_data)))
        img.save(f"db/pfps/{username}.jpg", format="JPEG")
        target_user.pfp = f"{username}.jpg"

    db_sess.commit()
    return {"message": "OK"}


def delete_user(username):
    abort_if_user_not_found(username)

    session = db_session.create_session()
    cur_user = current_user
    target_user = session.get(User, username)
    if cur_user != target_user and cur_user.username != "admin":
        raise PermissionError(f"No permission to delete {target_user.username}. as {cur_user.username}, you can only delete yourself")

    if target_user.pfp:
        os.remove(f"db/pfps/{target_user.username}.jpg")

    session.delete(target_user)
    session.commit()
    return {"message": "OK"}


def get_users() -> dict:
    session = db_session.create_session()
    users = session.query(User).all()
    return {'users': [user.to_dict(only=('username', 'displayname')) for user in users]}


def add_user(args):
    db_sess = db_session.create_session()

    username = args['username']
    if db_sess.get(User, username):
        raise FileExistsError(f"Username {username} already used by someone")

    user = User(username=username, displayname=args['displayname'])
    user.set_password(args['password'])

    if args.get("pfp"):
        img_data = args['pfp'].encode()
        img = Image.open(BytesIO(base64.b64decode(img_data)))
        img.save(f"db/pfps/{username}.jpg", format="JPEG")
        user.pfp = f"{username}.jpg"

    db_sess.add(user)
    db_sess.commit()
    return {'message': "OK"}


def abort_if_user_not_found(username):
    session = db_session.create_session()
    user = session.query(User).get(username)
    if not user:
        raise Exception(f"User {username} not found") # yes, if someone has an account, then that thingie where when logging in it doesn't tell you what specifically is wrong is useless


class UserLoginResource(Resource):
    def post(self):
        args = login_user_parser.parse_args()
        username = args["username"]
        password = args["password"]
        try:
            return make_response(jsonify(login_user_api(username, password)), 200)
        except Exception as e:
            abort(404, message=e)


class UserThisOneResource(Resource):
    @login_required
    def get(self):
        return get_one_user(current_user.username)


class UsersResource(Resource):
    def get(self, username):
        try:
            return jsonify(get_one_user(username))
        except Exception as e:
            abort(404, message=e)


    @login_required
    def put(self, username):
        args = edit_user_parser.parse_args()
        try:
            return jsonify(edit_user(username, args))
        except PermissionError as e:
            abort(400, message=e)
        except Exception as e:
            abort(404, message=e)


    @login_required
    def delete(self, username):
        try:
            return jsonify(delete_user(username))
        except PermissionError as e:
            abort(400, message=e)
        except Exception as e:
            abort(404, message=e)


class UsersListResource(Resource):
    def get(self):
        return jsonify(get_users())

    def post(self):
        args = add_user_parser.parse_args()
        try:
            return jsonify(add_user(args))
        except FileExistsError as e:
            abort(409, message=e)