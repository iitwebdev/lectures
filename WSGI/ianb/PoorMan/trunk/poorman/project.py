from paste.util import import_string
import routes
import pkg_resources
import sys
import inspect
import re
from wareweb import cgifields
import paste.request
from formencode import variabledecode
from paste.deploy.config import CONFIG, ConfigMiddleware
from paste import httpexceptions
from paste.exceptions import errormiddleware
from paste.evalexception.middleware import EvalException

class Project(object):

    # These modules get imported early on, and so they can
    # do side-effect operations.
    #import_modules = ['connect']
    import_modules = []

    _template_factories = {}
    _controllers = {}
    config = CONFIG

    def __init__(self, package_name,
                 default_template_type=None,
                 default_template_format='html',
                 controller_prefix=None):
        self.package_name = package_name
        self.urlmap = routes.Mapper()
        #self.middleware_factories = [errormiddleware.ErrorMiddleware]
        self.middleware_factories = [EvalException]
        self.default_template_type = default_template_type
        self.default_template_format = default_template_format
        if controller_prefix is None:
            controller_prefix = package_name + '.'
        self.controller_prefix = controller_prefix
        # Somehow this should handle changing SCRIPT_NAME and whatnot
        self.head_html = []

    def template_factory(self, type=None):
        if type is None:
            type = self.default_template_type
        if type not in self._template_factories:
            for entry in pkg_resources.iter_entry_points(
                'python.templating.engines', name=type):
                self._template_factories[type] = entry.load()
                break
            else:
                raise LookupError(
                    "The template factory %r could not be found"
                    % type)
        return self._template_factories[type]()

    def connect(self, *args, **kw):
        self.urlmap.connect(*args, **kw)
        self.urlmap.create_regs(['[a-zA-Z][a-zA-Z0-9_]*'])

    def add_middleware(self, middleware_factory):
        self.middleware_factories.append(middleware_factory)
        
    def init(self):
        for module_name in self.import_modules:
            module_name = self.package_name + '.' + module_name
            import_string.simple_import(module_name)

    def controller(self, **kw):
        def decorate(func):
            func.wsgi_application = WSGIController(self, func, **kw)
            return func
        return decorate

    def redirect(self, url):
        raise NotImplementedError

    def wsgi_entry_point(self, environ, start_response):
        path_info = environ.get('PATH_INFO')
        reqconfig = routes.request_config()
        reqconfig.environ = environ
        reqconfig.mapper = self.urlmap
        reqconfig.redirect = self.redirect
        result = self.urlmap.routematch(path_info)
        if result is None:
            # @@: Put this in the not found error
            msg = 'Did not match: %r\n' % path_info
            for route in self.urlmap.matchlist:
                msg += 'Regex: %s' % route.regexp
                if re.search(route.regexp, path_info):
                    msg += "  regex matches (but fails restriction)"
                msg += '\n'
            exc = httpexceptions.HTTPNotFound(comment=msg)
            return exc.wsgi_application(environ, start_response)
        vars, routeobj = result
        if vars.get('path_info'):
            match = routeobj.regmatch.match(path_info)
            pos = match.start('path_info')
            new_script_name = path_info[:pos]
            new_path_info = path_info[pos:]
            if not new_path_info.startswith('/'):
                new_path_info = '/'+new_path_info
                new_script_name = new_script_name.rstrip('/')
        else:
            new_script_name = path_info
            new_path_info = ''
        if new_path_info and not new_path_info.startswith('/'):
            assert new_script_name.endswith('/')
            new_script_name = new_script_name[:-1]
            new_path_info = '/' + new_path_info
        environ['SCRIPT_NAME'] += new_script_name
        environ['PATH_INFO'] = new_path_info
        environ['poorman.urlvars'] = vars
        environ['poorman.routeobj'] = routeobj
        wsgi_object = self.get_object(vars, routeobj)
        wsgi_app = self.get_wsgi_app(vars, wsgi_object)
        return wsgi_app(environ, start_response)
    
    def get_object(self, vars, routeobj):
        """
        Given the matching variables, find the object that it points
        to.  Typically this means finding the ``controller.action``
        module/object/method.
        """
        controller = vars['controller']
        if controller.startswith('egg:'):
            return self.get_egg_object(vars, routeobj)
        controller = self.controller_prefix + controller
        if vars.get('action'):
            if ':' not in controller:
                controller = controller + ':' + vars['action']
            else:
                controller = controller + '.' + vars['action']
        if ':' in controller:
            controller_mod, controller_name = controller.split(':', 1)
        else:
            controller_mod = controller
            controller_name = 'index'
        if controller_mod not in sys.modules:
            import_string.simple_import(controller_mod)
        controller_mod = sys.modules[controller_mod]
        obj = controller_mod
        for part in controller_name.split('.'):
            obj = getattr(obj, part)
        return obj

    def get_egg_object(self, vars, routeobj):
        vars = vars.copy()
        uri = vars.pop('controller')
        if vars.get('action') == 'index':
            # This gets set by default, but probably doesn't apply
            # if it is still the default.
            # @@: Maybe I should check if it was explicitly set.
            del vars['action']
        if 'path_info' in vars:
            del vars['path_info']
        assert uri.startswith('egg:')
        dist = uri[4:].strip()
        if '#' in dist:
            dist, ep_name = dist.split('#', 1)
        else:
            ep_name = 'main'
        ep = pkg_resources.load_entry_point(
            dist, 'paste.app_factory', ep_name)
        app = ep(self.config.copy(), **vars)
        return app

    def get_wsgi_app(self, vars, obj):
        """
        Convert an object into a WSGI application.  Right now it only
        looks for a .wsgi_application value on the object.
        """
        if hasattr(obj, 'wsgi_application'):
            return obj.wsgi_application
        else:
            return obj

    def paste_deploy_app(self, global_conf, **local_conf):
        """
        This is the method that implements [paste.app_factory]
        """
        conf = global_conf.copy()
        conf.update(local_conf)
        app = self.wsgi_entry_point
        app = ConfigMiddleware(app, conf)
        for middleware in self.middleware_factories:
            # They'll just have to pick it up from defaults...
            app = middleware(app, conf)
        return app

class WSGIController(object):

    def __init__(self, project, func, template_name=None,
                 template_type=None, fragment=False,
                 template_format=None, variabledecode=False):
        self.project = project
        self.func = func
        self.template_name = template_name
        self.template_type = template_type
        self.fragment = fragment
        self.template_format = (
            template_format or project.default_template_format)
        (self.func_args, self.func_varargs, self.func_varkw,
         self.func_defaults) = inspect.getargspec(self.func)
        self.variabledecode = variabledecode

    def __call__(self, environ, start_response):
        req = Request(environ, self)
        req.head_html.extend(self.project.head_html)
        req.set_header('Content-Type', 'text/html; charset=utf8')
        call_vars = dict(req.fields)
        call_vars.update(environ.get('poorman.urlvars', {}))
        if self.variabledecode:
            call_vars = variabledecode.variable_decode(call_vars)
        if not self.func_varkw:
            good = {}
            for name in call_vars:
                if name in self.func_args:
                    good[name] = call_vars[name]
            call_vars = good
        res = self.func(req, **call_vars)
        start_response(req.status, req.response_headers())
        if isinstance(res, basestring):
            res = [res]
        # @@: Should encode response here if necessary
        return res
    
    def fill_template(self, template_name, info):
        factory = self.project.template_factory(type=self.template_type)
        # @@: What's the point of this?
        #template = factory.load_template(template_name)
        result = factory.render(info, format=self.template_format,
                                fragment=self.fragment, template=template_name)
        return result

class Request(object):

    def __init__(self, environ, controller):
        self.environ = environ
        self.controller = controller
        self.fields = cgifields.Fields(
            paste.request.parse_formvars(environ))
        self.headers_out = {}
        self.cookies = {}
        if 'HTTP_COOKIE' in environ:
            cookies = paste.request.get_cookies(environ)
            for key in cookies.keys():
                self.cookies[key] = cookies[key].value
        self._cookies_out = {}
        self.status = '200 OK'
        self.head_html = []
        
    def add_javascript(self, href=None, content=None):
        if href:
            self.head_html.append(
                '<script type="text/javascript" src="%s"></script>'
                % href)
        if content:
            self.head_html.append(
                '<script type="text/javascript">\n%s\n</script>'
                % content)

    def add_css(self, href=None, content=None):
        if href:
            self.head_html.append(
                '<link type="stylesheet" type="text/css" href="%s" />'
                % href)
        if content:
            self.head_html.append(
                '<style type="text/css">\n%s\n</style>' % content)
        
    def response_headers(self):
        headers = []
        for name, value in self.headers_out.items():
            if isinstance(value, list):
                for v in value:
                    headers.append((name, v))
            else:
                headers.append((name, value))
        for cookie in self._cookies_out.values():
            headers.append(('Set-Cookie', cookie.header()))
        return headers

    def session__get(self):
        if 'paste.session.factory' in self.environ:
            sess = self.environ['paste.session.factory']()
        elif 'paste.flup_session_service' in self.environ:
            sess = self.environ['paste.flup_session_service'].session
        self.__dict__['session'] = sess
        return sess

    session = property(session__get)
    
    def set_cookie(self, cookie_name, value, path='/',
                   expires='ONCLOSE', secure=False):
        c = cookiewriter.Cookie(cookie_name, value, path=path,
                                expires=expires, secure=secure)
        self._cookies_out[cookie_name] = c

    def set_header(self, header_name, header_value):
        header_name = header_name.lower()
        if header_name == 'status':
            self.status = header_value
            return
        self.headers_out[header_name] = header_value

    def add_header(self, header_name, header_value):
        header_name = header_name.lower()
        if header_name == 'status':
            self.status = header_value
            return
        if self.headers_out.has_key(header_name):
            if not isinstance(self.headers_out[header_name], list):
                self.headers_out[header_name] = [self.headers_out[header_name],
                                             header_value]
            else:
                self.headers_out[header_name].append(header_value)
        else:
            self.headers_out[header_name] = header_value

    def render(self, template_name=None, stacklevel=1, **vars):
        if not vars:
            # @@: Should this just update vars?
            frame = sys._getframe(stacklevel)
            vars = frame.f_locals
        if template_name is None:
            # @@: This should pick up the package name too:
            frame = sys._getframe(stacklevel)
            mod_name = frame.f_globals['__name__']
            base_package = self.controller.project.package_name
            assert mod_name.startswith(base_package+'.'), (
                "Unexpected module %r (expected %s.*)"
                % (mod_name, base_package))
            mod_name = mod_name[len(base_package)+1:]
            mod_name = base_package + '.' + '/templates' + '/' + mod_name
            func_name = frame.f_code.co_name
            if func_name != 'index':
                template_name = mod_name + '-' + func_name
            else:
                template_name = mod_name
            print template_name
        vars.setdefault('project', self.controller.project)
        vars.setdefault('head_html', '\n'.join(self.head_html))
        return self.controller.fill_template(template_name, vars)
