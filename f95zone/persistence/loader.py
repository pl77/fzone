import pickle
import json


from f95zone.paths.pathmeta import PathMeta
from f95zone.novel.visual_novel import VisualNovel


class Loader(object):
    """
    Load pickled data
    """
    def __init__(self):
        self.paths = PathMeta()

    def read(self):
        picklepath = self.paths.cache / 'data0.pickle'
        if not picklepath.exists():
            with open(self.paths.cache / 'data0.pickle', 'wb'):
                pass
        with open(str(picklepath),  'rb') as file:
            content = file.read()
        return content

    def parse(self):
        content = self.read()
        try:
            content = pickle.loads(content)
        except EOFError:
            content = {}
        return content

    @property
    def content(self):
        return self.parse()

    def load_json(self):
        location = self.paths.cache / 'data0.json'
        if location.exists():
            with open(location, 'r') as file:
                data = json.loads(file.read())
            return data

    @property
    def json_friendly(self):
        vns = [x.data for x in self.content if isinstance(x, VisualNovel)]
        return vns
