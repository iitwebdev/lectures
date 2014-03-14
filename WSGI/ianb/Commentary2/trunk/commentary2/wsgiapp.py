from flatatompub.wsgiapp import make_app as make_flat_app
from paste.urlmap import URLMap
from paste.urlparser import StaticURLParser
from commentary2.filter import Filter

def make_app(global_conf, static_dir, data_dir):
    flat_app = make_flat_app(global_conf, data_dir=data_dir)
    map = URLMap()
    map['/_atompub'] = flat_app
    map['/_commentary'] = StaticURLParser(os.path.join(os.path.dirname(__file__), 'javascript'))
    static = StaticURLParser(static_dir)
    map[''] = Filter(static)
    return map
