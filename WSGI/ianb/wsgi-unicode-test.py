import webob
from paste.httpserver import serve
from paste.urlmap import URLMap
import cgi
import urllib

word = u'fran\xe7ais'

def encoding_app(environ, start_response):
    body = u'''<html><head>
<title>UTF8 app</title>
</head><body>
<pre>
encoding=ENCODING
SCRIPT_NAME=%(SCRIPT_NAME)s
PATH_INFO=%(PATH_INFO)s
QUERY_STRING=%(QUERY_STRING)s
</pre>
<div>
<a href="/?latin1">view in latin1</a>
| <a href="/">view in utf8</a><br>
example latin1: LATIN1_RAW  |  example utf8:  UTF8_RAW
</div>

The link:
<a href="/%(latin1)s">%(latin1)s</a><br>
In UTF8:
<a href="/%(utf8)s">%(utf8)s</a><br>
Unencoded:
<a href="/%(raw)s">%(raw)s</a>
(<a href="/LATIN1_RAW">latin1</a>, <a href="/UTF8_RAW">utf8</a>)
<br>

Form:
<form action="/%(raw)s" method="GET">
<input type="text" name="value" value="%(raw)s">
<input type="submit">
</form>

With encoding:
<form action="/%(raw)s" method="GET">
<input type="hidden" name="encoding" value="ENCODING">
<input type="text" name="value" value="%(raw)s">
<input type="submit">
</form>

</body></html>
''' % dict(
PATH_INFO=cgi.escape(repr(environ['PATH_INFO'])),
    SCRIPT_NAME=cgi.escape(repr(environ['SCRIPT_NAME'])),
    QUERY_STRING=cgi.escape(repr(environ['QUERY_STRING'])),
    latin1=urllib.quote(word.encode('latin1')),
    utf8=urllib.quote(word.encode('utf8')),
    raw=word)
    if 'latin1' in environ.get('QUERY_STRING',  ''):
        encoding = 'latin1'
    else:
        encoding = 'utf8'
    body = body.encode(encoding)
    body = body.replace('LATIN1_RAW', word.encode('latin1'))
    body = body.replace('UTF8_RAW', word.encode('utf8'))
    body = body.replace('ENCODING', encoding)
    start_response('200 OK', 
        [('Content-Type', 'text/html; charset=%s' % encoding)])
    return [body]

if __name__ == '__main__':
    serve(encoding_app)
