#from sqlobject import *
#from pylons.database import PackageHub
#hub = PackageHub("hreviewcollector")
#__connection__ = hub

import re
import os
from ohm import persist
from ohm import descriptors
from paste.deploy import CONFIG

# TODO: should really accept unicode characters:
name_re = re.compile(r'^[a-z][a-z0-9_-]+$', re.I)

whitespace_char_re = re.compile(r'[ \t\n]+')
bad_char_re = re.compile(r'[^a-z0-9_-]', re.I)
bad_start_char_re = re.compile(r'[^a-z]', re.I)

class Bundle(object):
    """
    Represents a potential content bundle.
    """

    def __init__(self, name, title, get__=False):
        assert name_re.search(name), (
            "Bad name: %r" % name)
        self.name = name
        if get__:
            # Just run from .get()
            return
        self.title = title

    @classmethod
    def all_bundles(cls):
        for fn in os.listdir(CONFIG['data_dir']):
            if name_re.search(fn):
                yield cls.get(fn)

    @classmethod
    def get(cls, name):
        obj = cls(name, title=None, get__=True)
        return obj

    @classmethod
    def name_from_title(cls, title):
        name = title
        while 1:
            assert name
            if bad_start_char_re.search(name[0]):
                name = name[1:]
            else:
                break
        name = whitespace_char_re.sub(' ', name)
        name = bad_char_re.sub('', name)
        return name

    @classmethod
    def exists(cls, name):
        return os.path.exists(cls._base_dir(name))

    @property
    def base_dir(self):
        dir = self._base_dir(self.name)
        if not os.path.exists(dir):
            os.mkdir(dir)
        return dir

    @classmethod
    def _base_dir(cls, name):
        return os.path.join(CONFIG['data_dir'], name.lower())

    urls = descriptors.json_converter(
        persist.file_property('urls.txt', default='[]'))

    title = persist.file_property('title.txt', encoding='utf8')
                         
    def __repr__(self):
        return '<%s %s %s urls=%r>' % (
            self.__class__.__name__, hex(abs(id(self)))[2:],
            self.name, self.urls)
