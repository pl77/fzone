import typing


import requests_html
import requests
from f95zone.paths.pathmeta import PathMeta


class Crawler(object):
    """
    Crawl for games in your watchlist
    """
    response_type = typing.Union[requests.Response, requests_html.HTMLResponse]

    def __init__(self, username: str, password: str):
        self.__username = username
        self.__password = password
        self.session = requests_html.HTMLSession()
        self.logged_in = False
        self.paths = PathMeta()

    @property
    def _api_ends(self) -> dict:
        ends = {
            'url': 'https://f95zone.to',
            'watchlist': 'https://f95zone.to/watched/threads?unread=0',
            'login': 'https://f95zone.to/login'
        }
        return ends

    def login(self) -> bool:
        page: Crawler.response_type = self.session.get(self._api_ends['login'])
        _xftoken: list = page.html.find('input[name="_xfToken"]')
        if _xftoken:
            _xftoken: requests_html.Element = _xftoken[0]
            _xftoken: str = _xftoken.attrs['value']
        else:
            self.logged_in = False
            return False
        payload = {
            'login': self.__username,
            'url': '',
            'password': self.__password,
            'password_confirm': '',
            'additional_security': '',
            'remember': 1,
            '_xfRedirect': '/',
            'website_code': '',
            '_xfToken': _xftoken
        }
        post_url = f'{self._api_ends["login"]}/login'
        response: Crawler.response_type = self.session.post(post_url, data=payload)
        assert response.ok
        assertion: Crawler.response_type = self.session.get(self._api_ends['url'])
        assertion: list = assertion.html.find('a[href="/account/"]>span[class="p-navgroup-linkText"]')
        if assertion:
            assertion: requests_html.Element = assertion[0]
            if self.__username in assertion.text:
                self.logged_in = True
                return True

    def get_watched_games(self) -> list:
        if not self.logged_in:
            assert self.login()
        content = list()
        watchlist_page: Crawler.response_type = self.session.get(self._api_ends['watchlist'])
        last_page: int = self.last_page_getter(watchlist_page)
        urls = [f'https://f95zone.to/watched/threads?unread=0&page={x}' for x in range(2, last_page + 1)]
        urls.insert(0, self._api_ends['watchlist'])
        for url in urls:
            page: Crawler.response_type = self.session.get(url)
            data: list = page.html.find('a[href$="unread"]')
            if data:
                for item in data:
                    temp = f'https://f95zone.to{item.attrs["href"]}'
                    content.append(temp)
        return content

    def get_game_data(self, url: str) -> dict:
        if not self.logged_in:
            assert self.login()
        response: Crawler.response_type = self.session.get(url)
        title: list = response.html.find('h1.p-title-value')
        if title:
            title: requests_html.Element = title[0]
            title: str = title.text
            title: str = title.replace(u'\xa0', u' ')
        tags: list = response.html.find('a.tagItem')
        if tags:
            temp = list()
            for item in tags:
                item: requests_html.Element
                temp.append(item.text)
            tags = temp
            del temp
        overview: list = response.html.find('div.bbWrapper')
        external_links: list = list()
        internal_links: list = list()
        images: list = list()
        if overview:
            overview: requests_html.Element = overview[0]
            article: list = overview.find('div[style="text-align: center"]')
            for idx, chunk in enumerate(article):
                if chunk.text.strip().lower().startswith('download'):
                    chunk = article.pop(idx)
                    links = chunk.find('a')
                    for link in links:
                        if "link--external" in link.attrs['class']:
                            external_links.append((link.text, link.attrs['href']))
                        elif "link--internal" in link.attrs['class']:
                            internal_links.append((link.text, link.attrs['href']))
                        elif "js-lbImage" in link.attrs['class']:
                            images.append(link.attrs['href'])
            overview: str = "\n".join([a.text for a in article])
            overview: str = overview.replace(u'\u200b', '')
        data = {
            'title': title,
            'tags': tags,
            'overview': overview,
            'external_links': external_links,
            'internal_links': internal_links,
            'images': images,
            'url': url
        }
        return data

    def add_watched_games(self, game_list):
        if not self.logged_in:
            assert self.login()
        content = list()
        payload = dict(_xfWithData=1,
                       _xfResponseType="json")
        for url in game_list:
            url_req = f"{url}watch"
            url_stub = url[18:]
            payload['_xfRequestUri'] = url_stub
            page: Crawler.response_type = self.session.get(url_req, data=payload)
            _xftoken: list = page.html.find('input[name="_xfToken"]')
            if _xftoken:
                _xftoken: requests_html.Element = _xftoken[0]
                _xftoken: str = _xftoken.attrs['value']
            payload['email_subscribe'] = 0
            payload['_xfToken'] = _xftoken
            page: Crawler.response_type = self.session.post(url_req, data=payload)
            if page.status_code == 200:
                content.append(url)
        return len(content)

    def dump(self) -> bool:
        content = self.get_watched_games()
        with open(str(self.paths.cache / 'watchlist'), 'w') as file:
            file.writelines((f'{x}\n' for x in content))
        return True

    @staticmethod
    def last_page_getter(page: typing.Union[requests_html.HTMLResponse, requests.Response]) -> int:
        pages = page.html.find('li>a[href^="/watched/threads?unread=0&page="]')
        max_: int = 2
        if pages:
            for item in pages:
                item: requests_html.Element
                text = int(item.text)
                if text > max_:
                    max_ = text
        return max_
