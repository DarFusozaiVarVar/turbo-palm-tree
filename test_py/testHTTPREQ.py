import requests

BASE_URL = 'http://127.0.0.1:8080'

r = requests.post(f'{BASE_URL}/addUserInfo')
print(f'POST /addUserInfo: {r.status_code}')
print(r.text)

r = requests.get(f'{BASE_URL}/testUsers')
print(f'GET /testUsers: {r.status_code}')
print(r.text)
