import re

class RegexDispatch(object):

    def __init__(self, regexes):
        self.regexes = regexes

    def __call__(self, environ, start_response):
        environ['myframework.base'] = environ['SCRIPT_NAME']
        path_info = environ.get('PATH_INFO', '')
        environ.setdefault('SCRIPT_NAME', '')
        for regex, app in self.regexes:
            if isinstance(regex, basestring):
                regex = re.compile(regex)
            match = regex.search(path_info)
            if not match:
                continue
            prefix = path_info[:match.end()]
            extra_path_info = path_info[match.end():]
            if extra_path_info and not extra_path_info.startswith('/'):
                continue
            environ['SCRIPT_NAME'] += prefix
            environ['PATH_INFO'] = extra_path_info
            environ['myframework.path_vars'] = match.groupdict()
            return app(environ, start_response)
        start_response('404 Not Found',
                       [('content-type', 'text/plain')])
        return ['not found']
    
