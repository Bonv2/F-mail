from data import db_session

from data.users import User
from data.emails import Email


def main():
    db_session.global_init("db/users.db")
    db_sess = db_session.create_session()

    user1 = User(username="user1", displayname="User 1")
    user1.set_password("hello")

    user2 = User(username="user2", displayname="User 2")
    user2.set_password("goodbye")

    db_sess.add(user1)
    db_sess.add(user2)
    db_sess.commit()

    sender = db_sess.query(User).filter(User.username == "user1").first()
    receiver = db_sess.query(User).filter(User.username == "user2").first()

    email = Email()
    email.sender = sender  # можно email.sender_username
    email.receiver = receiver  # можно email.receiver_username
    email.contents = "Hello World!"

    db_sess.add(email)
    db_sess.commit()


if __name__ == '__main__':
    main()