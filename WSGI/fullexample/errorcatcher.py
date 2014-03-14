import sys
import traceback
from cStringIO import StringIO


class ErrorCatcher(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except:
            exc_info = sys.exc_info()
            start_response('500 Server Error',
                           [('Content-type', 'text/plain')],
                           exc_info)
            out = StringIO()
            traceback.print_exception(exc_info[0], exc_info[1],
                                      exc_info[2], file=out)
            return [out.getvalue()]
