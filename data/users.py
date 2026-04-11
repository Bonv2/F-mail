import datetime
import sqlalchemy
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase

from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    username = sqlalchemy.Column(sqlalchemy.String,
                           primary_key=True, unique=True)
    displayname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    pfp = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                      default=datetime.datetime.now)

    inbox = orm.relationship("Email", back_populates="receiver", foreign_keys="[Email.receiver_username]")
    outbox = orm.relationship("Email", back_populates="sender", foreign_keys="[Email.sender_username]")

    def __repr__(self):
        return f"<User> {self.username} {self.displayname} {self.email}"

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)