import json


class VisualNovel(object):
    """
    A game
    """
    def __init__(self, name: str,
                 title_tags: list,
                 tags: list,
                 overview: str,
                 version: str,
                 developer: str,
                 url: str,
                 external_links: list,
                 internal_links: list,
                 images: list):
        self.name = name
        self.title_tags = title_tags
        self.tags = tags
        self.overview = overview
        self.version = version
        self.developer = developer
        self.url = url
        self.external_links = external_links
        self.internal_links = internal_links
        self.images = images

    def __repr__(self):
        string = (
            f'Name: {self.name}\n'
            f'Tags: {self.title_tags}\n'
            f'Fetishes: {self.tags}\n'
            f'Overview: {self.overview}\n'
            f'Version: {self.version}\n'
            f'Developer: {self.developer}\n'
            f'Link: {self.url}\n'
            )
        return string

    @property
    def data(self) -> dict:
        vn_data = {
            'name': self.name,
            'title_tags': self.title_tags,
            'tags': self.tags,
            'overview': self.overview,
            'version': self.version,
            'developer': self.developer,
            'url': self.url,
            'external_links': self.external_links,
            'internal_links': self.internal_links,
            'images': self.images
        }
        return vn_data

    @property
    def export(self):
        exportable = json.dumps(self.data, indent=4)
        return exportable
