import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase

from sqlalchemy_serializer import SerializerMixin


class Email(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'emails'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    contents = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    files = sqlalchemy.Column(sqlalchemy.String, nullable=True)  # base64 zip files perhaps?

    sender_username = sqlalchemy.Column(sqlalchemy.String,
                                 sqlalchemy.ForeignKey("users.username"))
    receiver_username = sqlalchemy.Column(sqlalchemy.String,
                               sqlalchemy.ForeignKey("users.username"))

    sender = orm.relationship("User", foreign_keys=[sender_username], back_populates="outbox")
    receiver = orm.relationship("User", foreign_keys=[receiver_username], back_populates="inbox")

    def __repr__(self):
        return f"<Mail> {self.id} {self.sender.username} {self.reciever.username}"