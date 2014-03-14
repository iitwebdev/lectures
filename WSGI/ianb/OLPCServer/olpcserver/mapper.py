from olpcserver.util import add_slash

class MapperApp(object):

    def __init__(self):
        self.applications = {}
        self.exact_applications = {}
        self.prefixes = None

    def add_application(self, prefix, application, exact=False):
        if exact:
            self.exact_applications[prefix] = application
        else:
            prefix = prefix.rstrip('/')
            self.applications[prefix] = application
            self.prefixes = None

    def resolve(self):
        prefixes = self.applications.items()
        prefixes.sort(key=lambda x: -len(x[0]))
        self.prefixes = prefixes

    def __call__(self, environ, start_response):
        prefixes = self.prefixes
        if prefixes is None:
            self.resolve()
            prefixes = self.prefixes
        script_name = environ.get('SCRIPT_NAME', '')
        path_info = environ.get('PATH_INFO', '')
        if path_info in self.exact_applications:
            return self.exact_applications[path_info](environ, start_response)
        for prefix, app in prefixes:
            if prefix == path_info:
                return add_slash(environ, start_response)
            if path_info.startswith(prefix + '/'):
                script_name += prefix
                path_info = path_info[len(prefix):]
                environ['SCRIPT_NAME'] = script_name
                environ['PATH_INFO'] = path_info
                return app(environ, start_response)
        return self.not_found(environ, start_response)
    
    def not_found(self, environ, start_response):
        body = 'No handler given for the resource at <code>%(SCRIPT_NAME)s%(PATH_INFO)s'
        start_response('404 Not Found', [
            ('Content-Type', 'text/plain'),
            ('Content-Length', str(len(body)))])
        return [body]

