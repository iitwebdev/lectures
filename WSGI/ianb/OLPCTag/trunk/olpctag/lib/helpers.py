"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from pylons.helpers import log
from pylons.i18n import get_lang, set_lang
from pylons import request
from paste.url import URL as _URL

def static_file(filename):
    base = request.environ['olpctag.base_path']
    if not filename.startswith('/'):
        filename = '/' + filename
    if base.endswith('/'):
        base = base[:-1]
    return base + filename

def url(*args, **kw):
    base = _URL.from_environ(request.environ)
    return base(*args, **kw)
