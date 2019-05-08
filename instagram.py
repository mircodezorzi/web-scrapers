BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
QUERY_COMMENTS_JSON = '{{"shortcode":"{0}","first":50,"after":"{1}"}}'
QUERY_COMMENTS_URL = BASE_URL + 'graphql/query/?query_hash=33ba35852cb50da46f5b5e889df7d159'
QUERY_MEDIA_JSON = 'variables={{"id":"{}","first":{},"after":"{}"}}'
QUERY_MEDIA_URL  = BASE_URL + '/graphql/query/?query_hash=472f257a40c653c64c666ce877d59d2b'
USER_URL = BASE_URL + '{0}/?__a=1'

DELAY = 3
MAX_RETRIES = 10
STEPS = 100
TIMEOUT_DELAY = 5

cookies = ''

import json
import requests
import time
import re

class Logger:

    _DEBUG = 0
    _INFO  = 1
    _WARN  = 2
    _ERROR = 3
    _FATAL = 4

    def __init__(self, level):
        self.level = level

    def debug(self, message):
        if self.level <= self._DEBUG: print(message)

    def info(self, message):
        if self.level <= self._INFO:  print(message)

    def warn(self, message):
        if self.level <= self._WARN:  print(message)

    def error(self, message):
        if self.level <= self._ERROR: print(message)

    def fatal(self, message):
        if self.level <= self._FATAL: print(message)

class Scraper(Logger):

    def __init__(self, level):
        self.session = requests.Session()
        self.headers = {}
        self.level = level

    def get(self, **kwargs):
        for i in range(0, MAX_RETRIES):
            try:
                with self.session.get(**kwargs) as response:
                    if response.status_code is not 200:
                        self.error('Invalid response status code: %s' % response.status_code)
                        raise
                    return response
            except (requests.exceptions.ConnectionError,
                    requests.exceptions.MissingSchema):
                self.fatal('Invalid url or schema')
            except:
                time.sleep(TIMEOUT_DELAY)


    def get_json(self, **kwargs):
        try:
            with self.get(**kwargs) as response:
                if response: return response.json()
                raise
        except json.decoder.JSONDecodeError:
            print('Invalid response json')

    def download_image(self, url, path):
        img = self.get(url).content
        with open(path, 'wb') as f:
            f.write(img)

class Instagram(Scraper):

    def __init__(self, level):
        super().__init__(level)

        self.headers = {
'Host': 'www.instagram.com',
'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding': 'gzip, deflate, br',
'Connection': 'keep-alive',
'Cookie': f'{cookies}',
'Upgrade-Insecure-Requests': '1',
'DNT': '1',
'Cache-Control': 'max-age=0',
'TE': 'Trailers',
}

        self.end_cursor = ''

    def _get_user(self, username):
        user = self.get_json(url = USER_URL.format(username), headers = self.headers)
        self.debug('Succesfully queried user info')
        self.end_cursor = self._get_user_endcursor(user)
        if self.end_cursor:
            return self._get_user_media(user['graphql']['user']['id'], user)
        return user['graphql']['user']['edge_owner_to_timeline_media']['edges']

    def _get_user_media(self, user_id, firstr):
        media = firstr['graphql']['user']['edge_owner_to_timeline_media']['edges']
        while self.end_cursor:
            response = self.get_json(
                url = QUERY_MEDIA_URL,
                params = QUERY_MEDIA_JSON.format(user_id, STEPS, self.end_cursor),
                headers = self.headers)
            self.end_cursor = self._get_user_endcursor(response)
            [media.append(i) for i in response['data']['user']['edge_owner_to_timeline_media']['edges']]
            print(len(media))
            time.sleep(DELAY)
        return media

    def _get_user_endcursor(self, json):
        try:
            if json['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']:
                return json['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        except (KeyError, TypeError):
            if json['graphql']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']:
                return json['graphql']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']

    def _parse_media_mentions(self, media):
        try:
            caption = media['node']['edge_media_to_caption']['edges'][0]['node']['text']
            return re.findall('([@#]\w+)+', caption)
        except:
            return ''

    def _get_media_comments(self, shortcode):
        return self.get_json(
            url = QUERY_COMMENTS_URL,
            params = QUERY_COMMENTS_JSON.format(shortcode, 1),
            headers = self.headers)


if __name__ == '__main__':
    scraper = Instagram(0)
    s = scraper._get_user(input('username: '))
    with open('mentions', 'w') as f:
        [f.write('\n'.join(scraper._parse_media_mentions(_)) + '\n') for _ in s]
