import config

from google.appengine.ext import db
from unique import Unique

class Shareable(db.Model):
    """Base DB model for shareable gallery data."""
    date = db.DateTimeProperty(auto_now_add=True)
    hash = db.StringProperty()

    def __init__(self, *args, **kwargs):
        super(Shareable, self).__init__(*args, **kwargs)
        if not self.hash:
            index = Unique.new(Shareable.__name__, config.SHARE_INDEX_GENERATOR, 10)
            self.hash = config.SHARE_HASH_GENERATOR(index)

    @property
    def share_url(self):
        return config.SHARE_URL_TEMPLATE.substitute({ 'hash': self.hash })

    def to_dict(self):
        dict_properties = ['hash', 'share_url']
        dict_properties.extend(self.dict_properties)
        return dict([(p, unicode(getattr(self, p))) for p in dict_properties])

class Album(Shareable):
    """DB model for a shareable gallery album."""
    album_id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)

    dict_properties = ['album_id', 'name', 'url', 'assets']

    @property
    def url(self):
        return config.ALBUM_URL_TEMPLATE.substitute({ 'album_id': self.album_id })

    @property
    def assets(self):
        return [config.IMAGE_RELATIVE_URL, ]

class Image(Shareable):
    """DB model for a shareable gallery image."""
    album = db.ReferenceProperty(Album, required=True)
    image_id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    extension = db.StringProperty(required=True)
    image_data = db.BlobProperty(required=True)

    dict_properties = ['image_id', 'name', 'url', 'file_url', 'share_file_url', 'size']

    @property
    def url(self):
        return config.IMAGE_URL_TEMPLATE.substitute({ 'album_id': self.album.album_id,
                                                      'image_id': self.image_id })

    @property
    def file_url(self):
        return config.IMAGE_URL_TEMPLATE.substitute({ 'album_id': self.album.album_id,
                                                      'image_id': self.image_id + self.extension })

    @property
    def share_file_url(self):
        return config.SHARE_URL_TEMPLATE.substitute({ 'hash': self.hash + self.extension })

    @property
    def size(self):
        return len(self.image_data) if self.image_data else 0
    
class APIUser(db.Model):
    """DB model for authorized user of gallery API."""
    api_key = db.StringProperty(required=True)
    api_secret = db.StringProperty(required=True)
    name = db.StringProperty()

