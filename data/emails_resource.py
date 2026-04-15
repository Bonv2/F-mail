from flask_restful import reqparse, abort, Resource
from flask import jsonify
from PIL import Image
import base64
import os
from io import BytesIO

from . import db_session
from .emails import Email

# add_user_parser = reqparse.RequestParser()
# add_user_parser.add_argument("username", required=True)
# add_user_parser.add_argument("displayname", required=True)
# add_user_parser.add_argument("password", required=True)
# add_user_parser.add_argument("pfp", required=False, type=str)


def abort_if_email_not_found(id):
    session = db_session.create_session()
    email = session.query(Email).get(id)
    if not email:
        abort(404, message=f"Email {id} not found")


class UsersResource(Resource):
    def get(self, username):
        ...


    def put(self, username):
        ...


    def delete(self, username):
        ...


class EmailsListResource(Resource):
    def get(self):
        ...

    def post(self):
        ...