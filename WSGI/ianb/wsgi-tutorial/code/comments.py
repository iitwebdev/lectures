import re
import cgi
from filter import HTMLFilter


class Comments(HTMLFilter):

    def __init__(self, app):
        super(Comments, self).__init__(app)
        self.comment_data = {}

    def __call__(self, environ, start_response):
        if environ.get('PATH_INFO', '').startswith('/_comment/'):
            return self.comment_app(environ, start_response)
        else:
            return super(Comments, self).__call__(environ, start_response)

    def filter(self, script_name, path_info, environ,
               status, headers, body):
        match = re.search(r'</body>', body, re.IGNORECASE)
        if match:
            start, rest = body[:match.start()], body[match.start():]
        else:
            start, rest = body, ''
        body = (start + '\n'
                + self.comment_data.get(path_info, '')
                + self.comment_form(script_name, path_info)
                + rest)
        return status, headers, body

    def comment_form(self, script_name, path_info):
        return '''\
<form action="%(script_name)s/_comment/" method="POST">
<input type="hidden" name="path_info" value="%(path_info)s">
Comment:<br>
<textarea name="comment"></textarea><br>
<input type="submit" value="Comment">
</form>''' % locals()

    def comment_app(self, environ, start_response):
        fs = cgi.FieldStorage(environ=environ, fp=environ['wsgi.input'])
        path_info = fs['path_info'].value
        comment = fs['comment'].value
        comment = '<div>%s</div>\n' % comment
        self.comment_data[path_info] = self.comment_data.get(path_info, '') + comment
        location = environ['SCRIPT_NAME'] + path_info
        start_response('302 Found', [('content-type', 'text/plain'),
                                     ('location', location)])
        return ['redirect to ' + location]
