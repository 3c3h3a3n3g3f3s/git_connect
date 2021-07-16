import requests

url = 'http://127.0.0.1:5000/test'

rep = requests.post(url=url)

print(rep.content)
