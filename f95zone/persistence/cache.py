import pickle
import json


from f95zone.parsers.title import TitleParser
# from f95zone.parsers.overview import OverviewParser
from f95zone.parsers.watchlist import WatchlistParser
from f95zone.webclient.client import Client
from f95zone.paths.pathmeta import PathMeta
from f95zone.novel.visual_novel import VisualNovel
from f95zone.persistence.loader import Loader
from f95zone.crawler.crawler import Crawler


class Cache(object):
    def __init__(self):
        self.paths = PathMeta()
        self.client = Client()
        self.crawler = Crawler("None", "None")

    def generate_cache(self) -> list:
        novels = []
        watchlist = WatchlistParser(str(self.paths.watchlist)).watchlist
        for url in watchlist:
            raw_data: dict = self.crawler.get_game_data(url)
            title: dict = TitleParser(raw_data['title']).title
            # overview: str = OverviewParser(raw_data['overview']).overview  # (disabled until fix is issued)'None'  #
            game = {
                'name': title['name'],
                'title_tags': title.get('tags', None),
                'tags': raw_data['tags'],
                'version': title['version'],
                'developer': title['developer'],
                'overview': raw_data['overview'],
                'url': url,
                'external_links': raw_data['external_links'],
                'internal_links': raw_data['internal_links'],
                'images': raw_data['images'],
            }
            novels.append(VisualNovel(**game))
        return novels

    def dump(self, username: str, password: str, json_format: bool = True) -> bool:
        self.crawler = Crawler(username, password)
        data = self.generate_cache()
        if json_format:
            vns = [x.data for x in data if isinstance(x, VisualNovel)]
            with open(self.paths.cache / 'data0.json', 'w') as json_file:
                json_file.write(json.dumps(vns, indent=4))
        with open(self.paths.cache / 'data0.pickle', 'wb') as file:
            file.write(pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL))
        return True

    def export_to_json(self):
        data = Loader().json_friendly
        with open(self.paths.cache / 'data0.json', 'w') as json_file:
            json_file.write(json.dumps(data, indent=4))
