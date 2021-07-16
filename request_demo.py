import requests


url = 'http://127.0.0.1:5000/?name=name'
rep = requests.get(url=url)
print(rep.text)




