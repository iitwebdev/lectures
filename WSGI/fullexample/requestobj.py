import urllib
import cgi

class Request(object):

    def __init__(self, environ):
        self.environ = environ

    @property
    def params(self):
        if 'myframework.params' not in self.environ:
            fs = cgi.FieldStorage(environ=self.environ,
                                  fp=self.environ['wsgi.input'])
            params = {}
            for field in fs.list:
                if field.name in params:
                    if isinstance(params[field.name], list):
                        params[field.name].append(field.value)
                    else:
                        params[field.name] = [params[field.name], field.value]
                else:
                    params[field.name] = field.value
            self.environ['myframework.params'] = params
        return self.environ['myframework.params']
        
    @property
    def path_info(self):
        return self.environ['PATH_INFO']

    @property
    def method(self):
        return self.environ['REQUEST_METHOD']

    @property
    def request_url(self):
        environ = self.environ
        url = environ['wsgi.url_scheme']+'://'
        
        if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
        else:
            url += environ['SERVER_NAME']

        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        else:
            if environ['SERVER_PORT'] != '80':
                url += ':' + environ['SERVER_PORT']

        url += urllib.quote(environ.get('SCRIPT_NAME',''))
        url += urllib.quote(environ.get('PATH_INFO',''))
        if environ.get('QUERY_STRING'):
            url += '?' + environ['QUERY_STRING']
        return url

    def make_url(self, path, **vars):
        if vars:
            vars = urllib.urlencode(vars)
            if '?' in path:
                path += '&' + vars
            else:
                path += '?' + vars
        base = self.environ.get(
            'myframework.base', self.environ.get('SCRIPT_NAME', ''))
        url = base + '/' + path
        return url
