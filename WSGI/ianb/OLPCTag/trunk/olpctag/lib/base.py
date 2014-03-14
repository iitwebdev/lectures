from pylons import Response, c, g, cache, request, session
from pylons.controllers import WSGIController
from pylons.decorators import jsonify, validate
from pylons.templating import render, render_response
from pylons.helpers import abort, redirect_to, etag_cache
from pylons.i18n import N_, _, ungettext
import olpctag.models as model
import olpctag.lib.helpers as h
from paste.httpexceptions import *

class BaseController(WSGIController):
    # If not public, requires authentication:
    public = False
    title = None
    def __before__(self):
        auth = request.environ.get('HTTP_AUTHORIZATION')
        if auth:
            auth = auth.split(None, 1)[1]
            name, password = auth.decode('base64').split(':', 1)
            request.environ['REMOTE_USER'] = name
        if not self.public and not request.environ.get('REMOTE_USER'):
            raise HTTPUnauthorized(
                headers=[('WWW-Authenticate', 'Basic realm="Enter your username (password does not matter)"')])
        c.model = model
        try:
            c.group = self.group
        except KeyError:
            pass
        try:
            c.user = self.user
        except KeyError:
            pass
        if self.title is None:
            c.title = self.__class__.__name__[:-len('Controller')]
        else:
            c.title = self.title
            
    @property
    def user(self):
        try:
            return model.User.byUsername(request.environ['REMOTE_USER'])
        except LookupError:
            return model.User(username=request.environ['REMOTE_USER'])
    
    @property
    def group(self):
        return request.environ['olpctag.group']

    def __call__(self, environ, start_response):
        # Insert any code to be run per request here. The Routes match
        # is under environ['pylons.routes_dict'] should you want to check
        # the action or route vars here
        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
