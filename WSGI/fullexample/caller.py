from requestobj import Request


class wsgify(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, environ, start_response):
        args = environ.get('myframework.path_vars', {})
        request = Request(environ)
        response = request.response = Response()
        res_body = self.func(request, **args)
        if isinstance(res_body, Response):
            response, res_body = res_body, None
        start_response(response.status, response.headers)
        return response.make_body(res_body)


class Response(object):

    def __init__(self, body=None, status='200 OK',
                 headers=None, encoding='utf8'):
        if headers is None:
            headers = [('Content-type',
                        'text/html; charset=%s' % encoding)]
        self.headers = headers
        self.encoding = encoding
        self.status = status
        self.body = body

    def set_header(self, name, value):
        for check_name, check_value in self.headers:
            if check_name.lower() == name.lower():
                self.headers.remove((check_name, check_value))
        self.headers.append((name, value))

    def add_header(self, name, value):
        self.headers.append((name, value))

    def make_body(self, returned):
        if returned is None:
            assert self.body is not None
            returned = self.body
        if isinstance(returned, basestring):
            returned = [returned]
        for chunk in returned:
            if isinstance(chunk, unicode):
                chunk = chunk.encode(self.encoding)
            yield chunk
