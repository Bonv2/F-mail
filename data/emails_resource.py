from flask_restful import reqparse, abort, Resource
from flask_login import current_user, login_required
from flask import jsonify
from PIL import Image
import base64
import os
from io import BytesIO

from . import db_session
from .emails import Email
from .users import User

send_email_parser = reqparse.RequestParser()
send_email_parser.add_argument("receiver_username", required=True)
send_email_parser.add_argument("title", required=True)
send_email_parser.add_argument("contents", required=False)
send_email_parser.add_argument("files", required=False)


def get_one_email(id):
    abort_if_email_not_found(id)

    db_sess = db_session.create_session()
    email = db_sess.get(Email, id)
    if (email.sender != current_user and email.receiver != current_user) and current_user.username != "admin":
        raise Exception("Email not found or you don't have permission to see it")

    email_dict = email.to_dict(only=("id", "title", "contents", "files", "sender_username", "receiver_username"))
    return {'emails': [email_dict]}


def delete_email(id):
    abort_if_email_not_found(id)

    db_sess = db_session.create_session()
    email = db_sess.get(Email, id)
    if (email.sender != current_user and email.receiver != current_user) and current_user.username != "admin":
        raise Exception("Email not found or you don't have permission to see it")

    db_sess.delete(email)
    db_sess.commit()
    return {"messsage": "success"}


def get_emails():
    db_sess = db_session.create_session()
    emails = db_sess.query(Email).filter((Email.receiver == current_user) | (Email.sender == current_user)).all()
    return {'emails': [email.to_dict(only=("id", "title", "contents", "sender_username", "receiver_username")) for email in emails]}


def send_email(args):
    # sender is ofc the current user
    db_sess = db_session.create_session()
    receiver_username = args['receiver_username']
    receiver = db_sess.get(User, receiver_username)
    if not receiver:  # proper mail services allow you to send to non-existent addresses, we are not one of them
        raise Exception(f"Receiver {receiver_username} not found")
    if receiver == current_user:
        raise Exception("Receiver can't be current user")
    title = args['title']

    letter = Email(sender=current_user, receiver=receiver, title=title)
    if args.get("contents"):
        letter.contents = args["contents"]
    if args.get("files"):
        letter.files = args["files"]

    db_sess.merge(letter)
    db_sess.commit()
    return {"id": letter.id}


def abort_if_email_not_found(id):
    session = db_session.create_session()
    email = session.query(Email).get(id)
    if not email:
        raise Exception("Email not found or you don't have permission to see it")


class EmailsResource(Resource):
    @login_required
    def get(self, id):
        try:
            return jsonify(get_one_email(id))
        except Exception as e:
            abort(404, message=e)


    @login_required
    def delete(self, id):
        try:
            return jsonify(delete_email(id))
        except Exception as e:
            abort(404, message=e)


class EmailsListResource(Resource):
    @login_required
    def get(self):
        return jsonify(get_emails())

    @login_required
    def post(self):
        args = send_email_parser.parse_args()
        try:
            return jsonify(send_email(args))
        except Exception as e:
            print(e)
            abort(404, message=e)