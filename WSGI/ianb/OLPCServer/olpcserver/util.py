from rfc822 import parsedate_tz, mktime_tz, formatdate
from datetime import datetime, date, timedelta, tzinfo
import calendar
import time

__all__ = ['serialize_date', 'eval_import', 'simple_import', 'import_module']

############################################################
## Date handling:

def serialize_date(dt):
    if dt is None:
        return None
    if isinstance(dt, unicode):
        dt = dt.encode('ascii')
    if isinstance(dt, str):
        return dt
    if isinstance(dt, timedelta):
        dt = datetime.now() + dt
    if isinstance(dt, (datetime, date)):
        dt = dt.timetuple()
    if isinstance(dt, (tuple, time.struct_time)):
        dt = calendar.timegm(dt)
    if not isinstance(dt, (float, int)):
        raise ValueError(
            "You must pass in a datetime, date, time tuple, or integer object, not %r" % dt)
    return formatdate(dt)

def parse_date_timestamp(value):
    if not value:
        return None
    t = parsedate_tz(value)
    if t is None:
        # Could not parse
        return None
    t = mktime_tz(t)
    return t

## FIXME: not sure if I need this?
class _UTC(tzinfo):
    def dst(self, dt):
        return timedelta(0)
    def utcoffset(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return 'UTC'
    def __repr__(self):
        return 'UTC'
UTC = _UTC()

def parse_date(value):
    value = parse_date_timestamp(value)
    if value is not None:
        return datetime.fromtimestamp(t, UTC)

############################################################
## Importers:

def eval_import(s):
    """
    Import a module, or import an object from a module.

    A module name like ``foo.bar:baz()`` can be used, where
    ``foo.bar`` is the module, and ``baz()`` is an expression
    evaluated in the context of that module.  Note this is not safe on
    arbitrary strings because of the eval.
    """
    if ':' not in s:
        return simple_import(s)
    module_name, expr = s.split(':', 1)
    module = import_module(module_name)
    obj = eval(expr, module.__dict__)
    return obj

def simple_import(s):
    """
    Import a module, or import an object from a module.

    A name like ``foo.bar.baz`` can be a module ``foo.bar.baz`` or a
    module ``foo.bar`` with an object ``baz`` in it, or a module
    ``foo`` with an object ``bar`` with an attribute ``baz``.
    """
    parts = s.split('.')
    module = import_module(parts[0])
    name = parts[0]
    parts = parts[1:]
    last_import_error = None
    while parts:
        name += '.' + parts[0]
        try:
            module = import_module(name)
            parts = parts[1:]
        except ImportError, e:
            last_import_error = e
            break
    obj = module
    while parts:
        try:
            obj = getattr(module, parts[0])
        except AttributeError:
            raise ImportError(
                "Cannot find %s in module %r (stopped importing modules with error %s)" % (parts[0], module, last_import_error))
        parts = parts[1:]
    return obj

def import_module(s):
    """
    Import a module.
    """
    mod = __import__(s)
    parts = s.split('.')
    for part in parts[1:]:
        mod = getattr(mod, part)
    return mod

def add_info_to_exception(exc, message):
    if message.strip() == message:
        message = ' ' + message
    args = getattr(exc, 'args', None)
    if args is None:
        # Blast, can't do anything
        return
    if not args:
        arg0 = ''
    else:
        arg0 = args[0]
    arg0 = '%s%s' % (arg0, message)
    exc.args = (arg0,) + args[1:]

############################################################
## Little applications

def add_slash(environ, start_response):
    """
    Adds a slash to the request path (as an external redirect)
    """
    location = '%(wsgi.url_scheme)s://%(HTTP_HOST)s%(SCRIPT_NAME)s%(PATH_INFO)s/' % environ
    if environ['QUERY_STRING']:
        location += '?' + environ['QUERY_STRING']
    body = 'The resource has been redirected to %s' % location
    start_response('301 Moved Permanently', [
        ('Content-Type', 'text/plain'),
        ('Content-Length', str(len(body))),
        ('Location', location)])
    return [body]

