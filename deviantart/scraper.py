from urllib.request import urlopen, Request
import feedparser
import json
import time
import sys
import re
import os

html_index_beg = '<html><head><title>USERNAME</title><style>body{background-color:#d4dfd0;}ul{list-style-type:none;}li a{display:block;padding:16px;text-decoration:none;color:#000000;}h1 a{text-decoration:none;color:black;}</style></head><body><h1><a href="https://www.deviantart.com/USERNAME">USERNAME</a></h1><ul>'
html_index_end = '</ul></body></html>'
html_entry = '<li><a href="FILEPATH">TITLE</a></li>'
html_page  = '<html><head><title>TITLE</title><link rel="stylesheet" href="../../styles.css"></head><body><div class="container"><h2>TITLE</h2><div class="about">by <a href="https://www.deviantart.com/USERNAME">USERNAME</a>, DATE</div>MEDIA</div><div class="description">DESCRIPTION</div></body></html>'
html_lit   = '<div class="text">TEXT</div>'
html_img   = '<div class="image"><a href="../media/FILENAME.jpg"><img src="../media/FILENAME.jpg"></a></div>'

def download_entry(username, url, filename, date, description):
    filepath = '{}/posts/{}.html'.format(username, filename)

    t = html_page
    t = t.replace('TITLE', filename)
    t = t.replace('USERNAME', username)
    t = t.replace('DATE', date)
    t = t.replace('DESCRIPTION', description)

    if media_url.find('.net') > -1: # download image
        fp = '{}/media/{}.jpg'.format(username, filename)
        if not os.path.isfile(fp):
            print('downloading {}...'.format(filename))
            for i in range(10):
                try:
                    image = urlopen(url, timeout = 30).read()
                    break
                except:
                    time.sleep(3)
                    print('timedout')
            with open(fp, 'wb') as f:
                f.write(image)
            t = t.replace('MEDIA', html_img.replace('FILENAME', filename))
    else: # download literature
        if not os.path.isfile(filepath):
            print('downloading {}...'.format(filepath))
            req  = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urlopen(req).read().decode(encoding='iso-8859-1')
            text = re.search('text">\n(.*)<', html).group(1)
            t = t.replace('MEDIA', html_lit.replace('TEXT', text))

    with open(filepath, 'w') as f:
        f.write(t)

with open('usernames', 'r') as f:
    usernames = f.read().split('\n')[:-1]

for username in usernames:
    if username[0] == '#': continue
    t = html_index_beg.replace('USERNAME', username)
    url = 'http://backend.deviantart.com/rss.xml?q=gallery:{}&offset={}&limit={}'
    os.makedirs(username + '/posts', exist_ok=True)
    os.makedirs(username + '/media', exist_ok=True)
    steps  = 20
    offset = 0
    while True:
        feed = feedparser.parse(url.format(username, offset, steps))
        if not len(feed['entries']): break
        for entry in feed['entries']:
            media_url   = entry['media_content'][0]['url']
            filename    = entry['title']
            regex = re.compile('[\?&%#@/]')
            filename = regex.sub('', filename)
            description = entry['summary']
            date        = entry['published']
            download_entry(username, media_url, filename, date, description)
            if media_url.find('.net') > -1:
                t += html_entry.replace('FILEPATH', 'media/{}.jpg'.format(filename))\
                               .replace('TITLE', filename)
            else:
                t += html_entry.replace('FILEPATH', 'posts/{}.html'.format(filename))\
                               .replace('TITLE', filename)
        offset += steps
    with open('{}/index.html'.format(username), 'w') as f:
        f.write(t)
