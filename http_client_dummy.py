import requests

url = 'http://localhost:5000/video'
data = {'key': 'value'}  # example data

try:
    response = requests.post(url, json=data)
    print('Status Code:', response.status_code)
    print('Response:', response.text)
except requests.exceptions.ConnectionError as e:
    print('Connection failed:', e)
