import requests
from pprint import pprint

login_data = {
    "username": "user1",
    "password": "hello"
}

cookie = requests.post("http://127.0.0.1:5000/api/login", json=login_data).cookies

email_data = {
    "receiver_username": "user2",
    "title": "Best email service ever!!",
    "contents": "Email is just so trendy, and the ui is so 'well' polished!\nI love how i cant communicate with any other email service.",
}

result = requests.post("http://127.0.0.1:5000/api/emails", cookies=cookie, json=email_data)
try:
    print(result.json(), result.status_code)
except Exception as e:
    print(result.status_code)

result = requests.get("http://127.0.0.1:5000/api/emails", cookies=cookie)
pprint(result.json())