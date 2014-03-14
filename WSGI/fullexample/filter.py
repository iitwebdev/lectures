from cStringIO import StringIO

class Filter(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('SCRIPT_NAME', '')
        path_info = environ.get('PATH_INFO', '')
        sent = []
        written_response = StringIO()
        def replacement_start_response(status, headers, exc_info=None):
            if not self.should_filter(status, headers):
                return start_response(status, headers, exc_info)
            else:
                sent[:] = [status, headers, exc_info]
                return written_response.write
        app_iter = self.app(environ, replacement_start_response)
        if not sent:
            return app_iter
        status, headers, exc_info = sent
        try:
            for chunk in app_iter:
                written_response.write(chunk)
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()
        body = written_response.getvalue()
        status, headers, body = self.filter(
            script_name, path_info, environ, status, headers, body)
        start_response(status, headers, exc_info)
        return [body]

    def should_filter(self, status, headers):
        raise NotImplementedError
    
    def filter(self, status, headers, body):
        raise NotImplementedError

class HTMLFilter(Filter):

    def should_filter(self, status, headers):
        if not status.startswith('200'):
            return False
        for name, value in headers:
            if name.lower() == 'content-type':
                return value.startswith('text/html')
        return False
