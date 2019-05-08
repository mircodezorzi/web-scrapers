import requests
import time
import re

url = 'https://pastebin.com/archive'
r = requests.get(url)
pastes = sorted(re.findall(
    '<a href="/([A-Za-z0-9]+)">.+</a>',
    r.content.decode())[2:-9], key = lambda x: len(x))[1:]
print(pastes)

for paste in pastes:
    url = 'https://pastebin.com/raw/{}'.format(paste)
    r = requests.get(url)
    with open('tmp/{}'.format(paste), 'w') as f:
        f.write(r.content)
    time.sleep(1)
