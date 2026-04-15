import requests

login_attempt = {
    "username": "user1",
    "password": "hello"
}

result = requests.post('http://127.0.0.1:5000/api/login', json=login_attempt)

print(result.status_code)
try:
    print(result.json())
except Exception:
    pass
print(result.cookies)

cookiess = result.cookies

edit_attempt = {
    "username": "user1",
}
result = requests.put('http://127.0.0.1:5000/api/users/user2', json=edit_attempt, cookies=cookiess)
print(result.status_code)
try:
    print(result.json())
except Exception:
    pass