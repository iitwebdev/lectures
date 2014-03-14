from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext
import hreviewcollector.models as model
import hreviewcollector.lib.helpers as h
from paste.url import URL
from Cookie import SimpleCookie

class BaseController(WSGIController):

    title = None
    
    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        self._cookies = SimpleCookie()
        def repl_start_response(status, headers, exc_info=None):
            for c in self._cookies.values():
                
                headers.append(
                    'Set-Cookie', c.output(header=''))
            return start_response(status, headers, exc_info)
        return WSGIController.__call__(self, environ, repl_start_response)

    def __before__(self):
        request.charset = 'utf8'
        c.self = self
        if self.title is None:
            c.title = self.__class__.__name__[:-len('Controller')]
        else:
            c.title = self.title
        c.url = URL.from_environ(
            request.environ,
            script_name=request.environ['paste.recursive.script_name'],
            with_path_info=False)
        c.session = session
        if 'bundle' in request.urlvars:
            self.bundle = model.Bundle.get(request.urlvars['bundle'])
            c.bundle_url = c.url[self.bundle.name]
        else:
            self.bundle = None
            c.bundle_url = None
        if request.cookies.get('flash'):
            c.flash = request.cookies['flash']
            self.delete_cookie('flash')
        else:
            c.flash = None

    def flash(self, msg):
        self.set_cookie('flash', msg)

    def set_cookie(self, key, value='', **kw):
        kw.setdefault('path', '/')
        self._cookies[key] = value
        for var_name, var_value in kw.items():
            if var_value is not None and var_value is not False:
                self._cookies[key][var_name.replace('_', '-')] = var_value

    def delete_cookie(self, key, path='/', domain=None):
        self.set_cookie(key, '', path=path, domain=domain,
                        expires=0, max_age=0)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
