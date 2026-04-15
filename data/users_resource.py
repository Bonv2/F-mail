from flask_login import current_user, login_user, logout_user, login_required
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


def abort_if_user_not_found(username):
    session = db_session.create_session()
    user = session.query(User).get(username)
    if not user:
        abort(404, message=f"User {username} not found")


class UserLoginResource(Resource):
    def post(self):
        args = login_user_parser.parse_args()
        username = args["username"]
        password = args["password"]
        db_sess = db_session.create_session()
        user = db_sess.get(User, username)
        if not user:
            abort(404, message=f"Incorrect username or password")
        if user.check_password(password):
            login_user(user)
            return make_response(jsonify({"success": "success, check cookies"}), 200)
        abort(404, message=f"Incorrect username or password")


class UsersResource(Resource):
    def get(self, username):
        abort_if_user_not_found(username)
        session = db_session.create_session()
        user = session.get(User, username)
        user_dict = user.to_dict(only=('username', 'displayname'))
        try:
            with open(user.pfp, "rb") as f:
                pfp = f.read()
            user_dict["pfp"] = base64.b64encode(pfp).decode()
        except Exception as e:
            pass
        return jsonify({
            'users': [user_dict]
        })

    @login_required
    def put(self, username):
        abort_if_user_not_found(username)
        db_sess = db_session.create_session()

        args = edit_user_parser.parse_args()
        cur_user = current_user
        target_user = db_sess.get(User, username)
        if cur_user != target_user and cur_user.username != "admin":
            abort(400, message=f"No permission to edit {target_user.username}, as {cur_user.username}, you can only edit yourself")
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
        return jsonify({"success": "OK"})

    @login_required
    def delete(self, username):
        abort_if_user_not_found(username)

        session = db_session.create_session()
        cur_user = current_user
        target_user = session.get(User, username)
        if cur_user != target_user and cur_user.username != "admin":
            abort(400, message=f"No permission to delete {target_user.username}, as {cur_user.username}, you can only delete yourself")

        if target_user.pfp:
            os.remove(f"db/pfps/{target_user.username}.jpg")

        session.delete(target_user)
        session.commit()
        return jsonify({"success": "OK"})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({
            'users': [user.to_dict(only=('username', 'displayname')) for user in users]
        })

    def post(self):
        args = add_user_parser.parse_args()
        db_sess = db_session.create_session()

        username = args['username']
        if username in [i[0] for i in db_sess.query(User.username).all()]:
            abort(409, message="Username already used by someone")

        user = User(username=username, displayname=args['displayname'])
        user.set_password(args['password'])

        if args.get("pfp"):
            img_data = args['pfp'].encode()
            img = Image.open(BytesIO(base64.b64decode(img_data)))
            img.save(f"db/pfps/{username}.jpg", format="JPEG")
            user.pfp = f"{username}.jpg"

        db_sess.add(user)
        db_sess.commit()
        return jsonify({'username': user.username})