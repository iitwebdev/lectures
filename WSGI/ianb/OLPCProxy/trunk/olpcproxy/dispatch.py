"""
Dispatch to static files, or to the main proxy
"""

from paste.request import path_info_pop, construct_url
from paste.urlparser import StaticURLParser
import os
from olpcproxy.proxy import make_olpc_proxy
from olpcproxy.model import Storage

here = os.path.dirname(__file__)
static_dir = os.path.join(here, 'public')
static_app = StaticURLParser(static_dir)

class Dispatcher(object):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        self.store = Storage(self.data_dir)
        self.proxy = make_olpc_proxy(self.store)

    def __call__(self, environ, start_response):
        path_info = environ.setdefault('PATH_INFO', '')
        if path_info.startswith('/.olpcproxy/'):
            path_info_pop(environ)
            return static_app(environ, start_response)
        environ['olpcproxy.static_url'] = construct_url(environ, path_info='/.olpcproxy', with_query_string=False)
        environ['olpcproxy.static_path'] = static_dir
        return self.proxy(environ, start_response)
    
