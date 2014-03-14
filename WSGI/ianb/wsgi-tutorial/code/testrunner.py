import urllib
from cStringIO import StringIO

def send_request(app, path_info, method='GET',
                 body='', environ={}):
    environ = make_environ(
        path_info, method, body, environ)
    sent = []
    output = StringIO()
    def start_response(status, headers, exc_info=None):
        sent[:] = [status, headers]
        return output.write
    app_iter = app(environ, start_response)
    try:
        for chunk in app_iter:
            output.write(chunk)
    finally:
        if hasattr(app_iter, 'close'):
            app_iter.close()
    status, headers = sent
    return TestResponse(status, headers, output.getvalue(),
                        environ['wsgi.errors'].getvalue(),
                        environ)

def make_environ(path_info, method, body, environ):
    environ = environ.copy()
    if body:
        if not isinstance(body, str):
            body = urllib.urlencode(body)
    else:
        body = ''
    environ['wsgi.input'] = StringIO(body)
    environ['CONTENT_LENGTH'] = len(body)
    environ['wsgi.errors'] = StringIO()
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.multithread'] = False
    environ['wsgi.multiprocess'] = False
    environ['wsgi.run_once'] = False
    environ['wsgi.url_scheme'] = 'http'
    if '?' in path_info:
        path_info, qs = path_info.split('?', 1)
    else:
        qs = ''
    environ['PATH_INFO'] = path_info
    environ['QUERY_STRING'] = qs
    environ['REQUEST_METHOD'] = method
    environ['SCRIPT_NAME'] = ''
    environ['SERVER_PORT'] = '80'
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'
    environ['SERVER_NAME'] = environ['HTTP_HOST'] = 'localhost'
    return environ

class TestResponse(object):

    def __init__(self, status, headers, body, errors, environ):
        self.status = status
        self.headers = headers
        self.body = body
        self.errors = errors
        self.environ = environ

    def __repr__(self):
        return '<%s %s from %s%s (%i bytes)>' % (
            self.__class__.__name__,
            self.status,
            self.environ['SCRIPT_NAME'],
            self.environ['PATH_INFO'],
            len(self.body))

    def __str__(self):
        out = StringIO()
        out.write(self.status+'\n')
        for name, value in self.headers:
            name = name.title()
            out.write('%s: %s\n' % (name, value))
        for line in self.body.splitlines(True):
            if line.strip():
                out.write(line)
        if self.errors:
            out.write('-- Errors: --\n')
            out.write(self.errors)
        return out.getvalue()
