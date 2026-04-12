from flask_restful import reqparse, abort, Resource
from flask import jsonify
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
edit_user_parser.add_argument("password", required=True)
edit_user_parser.add_argument("pfp", required=False, type=str)

delete_user_parser = reqparse.RequestParser()
delete_user_parser.add_argument("password", required=True)


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
            user_dict["pfp"] = base64.b64encode(pfp).decode()
        except Exception as e:
            pass
        return jsonify({
            'users': [user_dict]
        })


    def put(self, username):
        abort_if_user_not_found(username)
        db_sess = db_session.create_session()

        args = edit_user_parser.parse_args()
        password = args["password"]
        user = db_sess.get(User, username)
        if not user.check_password(password):
            abort(404, message="Incorrect password")
        if args["displayname"]:
            user.displayname = args["displayname"]
        if args["pfp"]:
            pfp_path = f"db/pfps/{user.username}"
            if os.path.exists(pfp_path):
                os.remove(f"db/pfps/{user.username}.jpg")
            img_data = args['pfp'].encode()
            img = Image.open(BytesIO(base64.b64decode(img_data)))
            img.save(f"db/pfps/{username}.jpg", format="JPEG")
            user.pfp = f"{username}.jpg"

        db_sess.commit()
        return jsonify({"success": "OK"})


    def delete(self, username):
        abort_if_user_not_found(username)
        args = delete_user_parser.parse_args()

        session = db_session.create_session()
        user = session.get(User, username)
        if not user.check_password(args["password"]):
            abort(404, message="Incorrect password")

        if user.pfp:
            os.remove(f"db/pfps/{user.username}.jpg")

        session.delete(user)
        session.commit()
        return jsonify({"success": "OK"})


class UsersListResource(Resource):
    def get(self):
        ...

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