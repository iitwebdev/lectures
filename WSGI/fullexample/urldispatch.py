class URLDispatch(object):

    def __init__(self, app_list):
        self.app_list = app_list

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        for prefix, app in self.app_list:
            if prefix.endswith('/'):
                prefix = prefix[:-1]
            if path_info.startswith(prefix+'/'):
                environ['SCRIPT_NAME'] = (
                    environ.get('SCRIPT_NAME', '') + prefix)
                environ['PATH_INFO'] = path_info[len(prefix):]
                return app(environ, start_response)
        start_response('404 Not Found',
                       [('content-type', 'text/plain')])
        return ['not found']

    
