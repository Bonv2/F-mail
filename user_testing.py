import requests

import base64


def bytes_to_base64(bytes) -> str:
    return base64.b64encode(bytes).decode()


def main():
    with open("test_image.png", "rb") as f:
        pfp = bytes_to_base64(f.read())

    user1 = {"username": "user1", "displayname": "User 1st", "password": "hello"}
    user2 = {"username": "user2", "displayname": "User 2nd", "password": "goodbye", "pfp": pfp}

    add_user1 = requests.post("http://127.0.0.1:5000/api/users", json=user1)
    try:
        print(add_user1.json(), add_user1.status_code)
    except Exception:
        pass
    add_user2 = requests.post("http://127.0.0.1:5000/api/users", json=user2)
    try:
        print(add_user2.json(), add_user2.status_code)
    except Exception:
        pass

    user1_put = {"pfp": pfp}
    edit_user1 = requests.put("http://127.0.0.1:5000/api/users/user1", json=user1_put)
    try:
        print(edit_user1.json(), edit_user1.status_code)
    except Exception:
        pass
    print("this was supposed to fail, as we provided no authorization")

    login_request = requests.post("http://127.0.0.1:5000/api/login", json={"username": "user1", "password": "hello"})
    cookies = login_request.cookies
    print("we got the session cookies, below is response with them")

    user1_put = {"pfp": pfp}
    edit_user1 = requests.put("http://127.0.0.1:5000/api/users/user1", json=user1_put, cookies=cookies)
    try:
        print(edit_user1.json(), edit_user1.status_code)
    except Exception:
        pass


if __name__ == '__main__':
    main()