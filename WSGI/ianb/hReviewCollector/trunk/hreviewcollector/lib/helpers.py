"""
Helper functions

All names available in this module will be available under the Pylons h object.
"""
from webhelpers import *
from webhelpers import redirect_to as base_redirect_to
from pylons.helpers import log
from pylons.i18n import get_lang, set_lang
from hreviewcollector.lib.htmlrender import html

def redirect_to(*args, **kw):
    if not kw and len(args) == 1:
        args = (str(args[0]),)
    return base_redirect_to(*args, **kw)

def shorten(item, length=20):
    if len(item) > length:
        return item[:length-5]+"..."+item[-5:]
    else:
        return item

def format_size(bytes):
    if bytes > 100000:
        # Megabytes
        return '%.1fMb' % (bytes/1000000.0)
    elif bytes > 1000:
        return '%iKb' % (bytes/1000)
    elif bytes > 200:
        return '%.1fKb' % (bytes/1000.0)
    else:
        return '%ib' % bytes

        
