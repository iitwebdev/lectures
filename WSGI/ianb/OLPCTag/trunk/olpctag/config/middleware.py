from paste import httpexceptions
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from paste.registry import RegistryManager
from paste.deploy.config import ConfigMiddleware, CONFIG
from paste.deploy.converters import asbool

from pylons.error import error_template
from pylons.middleware import ErrorHandler, ErrorDocuments, StaticJavascripts, error_mapper
import pylons.wsgiapp

from olpctag.config.environment import load_environment
import olpctag.lib.helpers
import olpctag.lib.app_globals as app_globals
from paste.deploy.converters import asbool
from paste.request import path_info_pop, construct_url

import olpctag.models as model

def make_app(global_conf, full_stack=True, **app_conf):
    """Create a WSGI application and return it
    
    global_conf is a dict representing the Paste configuration options, the
    paste.deploy.converters should be used when parsing Paste config options
    to ensure they're treated properly.
    
    """
    # Setup the Paste CONFIG object
    CONFIG.push_process_config({'app_conf': app_conf,
                                'global_conf': global_conf})

    # Load our Pylons configuration defaults
    config = load_environment(global_conf, app_conf)
    config.init_app(global_conf, app_conf, package='olpctag')
        
    # Load our default Pylons WSGI app and make g available
    app = pylons.wsgiapp.PylonsApp(config, helpers=olpctag.lib.helpers,
                                   g=app_globals.Globals)
    g = app.globals
    app = GroupMiddleware(app)
    app = ConfigMiddleware(app, {'app_conf':app_conf,
        'global_conf':global_conf})
    
    # YOUR MIDDLEWARE
    # Put your own middleware here, so that any problems are caught by the error
    # handling middleware underneath
    
    # If errror handling and exception catching will be handled by middleware
    # for multiple apps, you will want to set full_stack = False in your config
    # file so that it can catch the problems.
    if asbool(full_stack):
        # Change HTTPExceptions to HTTP responses
        app = httpexceptions.make_middleware(app, global_conf)
    
        # Error Handling
        app = ErrorHandler(app, global_conf, error_template=error_template, **config.errorware)
    
        # Display error documents for 401, 403, 404 status codes (if debug is disabled also
        # intercepts 500)
        #app = ErrorDocuments(app, global_conf, mapper=error_mapper, **app_conf)

    # Establish the Registry for this application
    app = RegistryManager(app)
    
    static_app = StaticURLParser(config.paths['static_files'])
    print static_app
    javascripts_app = StaticJavascripts()
    app = Cascade([static_app, javascripts_app, app])
    return app


class GroupMiddleware(object):

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        conf = environ['paste.config']['app_conf']
        environ['olpctag.base_path'] = environ['SCRIPT_NAME'] or '/'
        if 'olpctag.group_info' not in environ:
            if 'group' in conf:
                group_info = {
                    'slug': conf['group'],
                    'name': conf.get('group.name'),
                    'description': conf.get('group.description'),
                    'uri': conf.get('group.uri'),
                    }
            if asbool(conf.get('auto_group')):
                next = path_info_pop(environ)
                if not next:
                    if environ['SCRIPT_NAME'].endswith('/') and not environ['PATH_INFO']:
                        environ['SCRIPT_NAME'] = environ['SCRIPT_NAME'][:-1]
                        environ['PATH_INFO'] = '/'
                    environ['olpctag.show_group_index'] = True
                    return self.app(environ, start_response)
                if not environ['PATH_INFO']:
                    # We went to /foo, need to redirect to /foo/
                    url = construct_url(environ, with_query_string=False)
                    url += '/'
                    if environ['QUERY_STRING']:
                        url += '?' + environ['QUERY_STRING']
                    exc = httpexceptions.HTTPMovedPermanently(
                        headers=[('Location', url)])
                    return exc(environ, start_response)
                group_info = {
                    'slug': next,
                    'name': None,
                    'description': None,
                    'uri': None,
                    }
            else:
                assert 0, "No group can be found"
            environ['olpctag.group_info'] = group_info
        else:
            group_info = environ['olpctag.group_info']
        try:
            g = model.Group.bySlug(group_info['slug'])
        except LookupError:
            g = model.Group(slug=group_info['slug'])
        for key in ['name', 'description', 'uri']:
            if group_info.get(key) and not getattr(g, key, None):
                setattr(g, key, group_info[key])
        environ['olpctag.group'] = g
        return self.app(environ, start_response)
