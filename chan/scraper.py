from urllib.request import urlopen, URLError
import datetime
import requests
import html
import json
import time
import os
import re

url_catalog = 'http://a.4cdn.org/{}/catalog.json'
url_posts   = 'http://a.4cdn.org/{}/thread/{}.json'
url_image   = 'http://i.4cdn.org/{}/{}{}'

boards = []

def create_dir(name):
    os.makedirs(str(name), exist_ok=True)

def get_timedate(posix):
    return datetime.datetime.utcfromtimestamp(posix).strftime('%D (%a) %T')

def get_boards():
    for board in boards:
        get_threads(board)

def get_threads(board):
    create_dir('{}/posts'.format(board))
    threads = requests.get(url_catalog.format(board))
    for page in threads.json():
        for thread in page['threads']:
            get_posts(board, thread)

def get_posts(board, thread):
    thread_id = thread['no']

    title = html.unescape(thread['sub'] if thread.get('sub') else str(thread_id))
    title = title.replace('/', '-')
    #if title in blacklist: return 0
    print('fetching {}/{}...'.format(board, title))
    create_dir('{}/media/{}'.format(board, thread_id))
    for _ in range(10):
        try:
            posts = requests.get(url_posts.format(board, thread_id), timeout=10)
            break
        except:
            time.sleep(2)
    posts = posts.json()['posts']
    download_html(board, thread_id, posts.copy(), title)
    for post in posts:
        if post.get('tim'):
            for _ in range(10):
                try:
                    downdload_media(board, thread_id, post)
                    break
                except:
                    pass

def downdload_media(board, thread_id, post):
    id  = post['tim']
    ext = post['ext']
    filepath = '{}/media/{}/{}{}'.format(board, thread_id, id, ext)
    if not os.path.isfile(filepath):
        print('downloading {}{}...'.format(id, ext))
        image = urlopen(url_image.format(board, id, ext), timeout = 30).read()
        with open(filepath, 'wb') as f:
            f.write(image)

html_template = '<html><head><meta http-equiv="Content-type" content="text/html; charset=utf-8"><title>TITLE</title><link rel="stylesheet" href="../styles.css"><script src="../../jquery.js"></script><script src="../../common.js"></script></head><body>HTML</body></html>'
op_template   = '<div id="NO" class="op clear"><div class="header"><div class="title">TITLE</div><div class="name">NAME</div><div class="date">DATE</div><div class="no">No. NO</div></div><div class="content">IMAGE<div class="text">COM</div></div></div>'
post_template = '<div id="NO" class="post clear"><div class="header"><div class="name">NAME</div><div class="date">DATE</div><div class="no">No. NO</div></div><div class="content">IMAGE<div class="text">COM</div></div></div>'
img_template  = '<div class="image_header">IMAGE_HEADER</div><a href="FILEPATH" target="_blank"><img class="image" src="FILEPATH"></a>'
#rep_template  = '<a href="NO" class="quotelink" style="">&gt;&gt;NO</a>'

def download_html(board, thread_id, posts, title):
    filepath = '{}/posts/{} ({}).html'.format(board, title, thread_id)

    out = ''

    op = posts.pop(0)
    t = op_template

    if op.get('tim'):
        t = t.replace('IMAGE',
            img_template\
                .replace('FILEPATH', '../media/{}/{}{}'.format(thread_id, op['tim'], op['ext']))\
                .replace('IMAGE_HEADER', '{}{}'.format(op['filename'], op['ext'])))
    else:
        t = t.replace('IMAGE', '')

    t = t.replace('COM',   op['com'] if op.get('com') else '')
    t = t.replace('NO',    str(op['no']))
    t = t.replace('TITLE', op['sub'] if op.get('sub') else '')
    t = t.replace('NAME',  op['name'] if op.get('name') else 'Anonymous')
    t = t.replace('DATE',  get_timedate(op['time']))

    out += t

    for post in posts:
        t = post_template
        if post.get('tim'):
            t = t.replace('IMAGE',
                img_template\
                    .replace('FILEPATH', '../media/{}/{}{}'.format(thread_id, post['tim'], post['ext']))\
                    .replace('IMAGE_HEADER', '{}{}'.format(post['filename'], post['ext'])))
        else:
            t = t.replace('IMAGE', '')

        t = t.replace('COM',  post['com'] if post.get('com') else '')
        t = t.replace('NO',   str(post['no']))
        t = t.replace('NAME', post['name'] if post.get('name') else 'Anonymous')
        t = t.replace('DATE', get_timedate(post['time']))
        out += t

    with open(filepath, 'w') as f:
        f.write(html_template.replace('TITLE', title).replace('HTML', out))

if __name__ == '__main__':
    get_boards()
