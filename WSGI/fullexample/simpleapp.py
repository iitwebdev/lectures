def simple_app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    return ['<html><head><title>Simple App</title></head>\n'
            '<body><h1>Simple App!</h1></body></html>']


def bad_app(environ, start_response):
    assert environ['REQUEST_METHOD'] == 'POST'
    return simple_app(environ, start_response)
