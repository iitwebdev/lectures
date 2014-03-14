import os
import posixpath
import mimetypes
from wsgiref.util import FileWrapper
from olpcserver.util import serialize_date, parse_date, add_slash

class StaticApp(object):

    def __init__(self, dir, max_age):
        self.dir = os.path.abspath(dir)
        self.max_age = max_age

    def __call__(self, environ, start_response):
        path = self.resolve_path(environ)
        if not os.path.exists(path):
            return self.not_found(environ, start_response, path)
        app = self.make_application(path)
        return app(environ, start_response)

    def make_application(self, path):
        return FileApp(path, self.max_age)

    def resolve_path(self, environ):
        path_info = environ.get('PATH_INFO', '')
        path_info = posixpath.normpath(path_info.lstrip('/'))
        if path_info == '.':
            path_info = ''
        path = os.path.join(self.dir, path_info)
        path = os.path.abspath(path)
        if not path.startswith(self.dir):
            # This should never happen
            raise OSError(
                "Path info %r resolves to file path %r (not below %r)"
                % (path_info, path, self.dir))
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')
        return path
    
    ## FIXME: these could actually happen to users; should be i18n'd:
    ## And Jinja'd?
    def not_found(self, environ, start_response, path):
        body = '''
        <html><head>
        <title>Not Found</title>
        </head><body>
        <h1>Not Found</h1>
        <p>The path %(SCRIPT_NAME)s%(PATH_INFO)s was not found.

        <p>(Looked in the file path %(path)s)</p>
        </body></html>
        ''' % dict(
            SCRIPT_NAME=environ.get('SCRIPT_NAME', ''),
            PATH_INFO=environ.get('PATH_INFO', ''),
            path=path)
        return simple_response(environ, start_response,
                               '404 Not Found', body)

    ## FIXME: should indexes actually be on?  Who are we to keep the
    ## kids from their own laptop content?
    def forbidden_dir(self, environ, start_response, path):
        body = '''
        <html><head>
        <title>Forbidden (Directory)</title>
        </head><body>
        <h1>Forbidden</h1>
        <p>The path %(SCRIPT_NAME)s%(PATH_INFO)s refers to a directory.</p>
        <p>You cannot view the listing through this interface</p>
        <p>(Looked in the file path %(path)s)</p>
        </body></html>
        ''' % dict(
            SCRIPT_NAME=environ.get('SCRIPT_NAME', ''),
            PATH_INFO=environ.get('PATH_INFO', ''),
            path=path)
        return simple_response(environ, start_response,
                               '403 Forbidden', body)

def simple_response(environ, start_response, status, body, content_type='text/html'):
    start_response(status, [
        ('Content-Type', content_type),
        ('Content-Length', str(len(body)))])
    return [body]

class FileApp(object):

    def __init__(self, path, mimetype=None, max_age=None):
        self.path = path
        self.max_age = max_age
        if mimetype is None:
            mimetype = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        self.mimetype = mimetype

    accept_methods = ['GET']

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD']
        if method not in self.accept_methods:
            body = 'Only the methods %s are allowed' % ', '.join(self.accept_methods)
            return simple_response(environ, start_response,
                                   '405 Method Not Allowed', body)
        return getattr(self, method)(environ, start_response)

    ## FIXME: This doesn't deal with Range requests
    ## FIXME: might also be nice to deal with gzipped content via Content-Encoding?
    def GET(self, environ, start_response):
        stat = os.stat(self.path)
        last_modified = stat.st_mtime
        not_modified = False
        if 'HTTP_IF_MODIFIED_SINCE' in environ:
            value = parse_date_timestamp(environ['HTTP_IF_MODIFIED_SINCE'])
            if value >= last_modified:
                not_modified = True
        etag = '%s-%s' % (last_modified, hash(self.path))
        if 'HTTP_IF_NONE_MATCH' in environ:
            value = environ['HTTP_IF_NONE_MATCH'].strip('"')
            if value == etag:
                not_modified = True
        headers = [
            ('Content-Type', self.mimetype),
            ('Content-Length', str(stat.st_size)),
            ('ETag', etag),
            ('Last-Modified', serialize_date(last_modified))]
        if self.max_age:
            headers.append(('Cache-control', 'max-age=%s' % self.max_age))
        if not_modified:
            start_response('304 Not Modified', headers)
            return []
        else:
            return self.serve_file(environ, start_response, headers)

    def serve_file(self, environ, start_response, headers):
        start_response('200 OK', headers)
        f = open(self.path, 'rb')
        return FileWrapper(f)
