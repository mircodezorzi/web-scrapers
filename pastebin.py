from urllib.request import urlopen
import re
import os
import time
import html

user = input('username: ')

page = 1
while True:
    url = 'https://pastebin.com/u/{}/{}'
    raw = urlopen(url.format(user, page)).read()
    if re.findall(b'has no public', raw):
        break
    print('fetched {}, page {}'.format(user, page))
    page += 1

    pastes = re.findall(b'\ <a href="\/([A-Za-z0-9]*)">(.*)</a>', raw)
    url = 'https://pastebin.com/{}'

    for i, paste in enumerate(pastes):

        id = paste[0].decode()
        try:
            title = paste[1].decode()
        except:
            title = paste[1].decode(encoding='iso-8859-1')
        title = html.unescape(title)
        title = title.replace('/', '-')

        if not os.path.isfile(title):
            print('\rdownloading pasta {} of {}'.format(i + 1, len(pastes)), end = '')
            raw = urlopen(url.format(id)).read().decode(encoding='iso-8859-1')
            start = raw.find('<textarea')
            start = raw.find('>', start)
            end = raw.find('</', start)
            text = raw[start + 1:end]
            with open(title, 'w') as f:
                f.write(html.unescape(text))
            time.sleep(1)
        else:
            print('\rskipping pasta {} of {}'.format(i + 1, len(pastes)), end = '')
    print()
    time.sleep(5)
