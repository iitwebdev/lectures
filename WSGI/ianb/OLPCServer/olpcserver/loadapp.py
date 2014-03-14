"""
Creates a single WSGI application from a config file.

The config file is an INI-style config file read by ConfigParser (with
substitutions).

Each section describes one application, like::

  [/path]
  files = /path/to/files/

This serve the static files ``/path/to/files/`` at
``http://localhost/path/``.  Each section serves an entire piece of
the path.

You may also give a section a name like ``[exact /favicon.ico]`` which
will serve up only that exact path.  Note that SCRIPT_NAME and
PATH_INFO will not be fixed up with this.

Any sections which do not start with ``/`` are ignored.  You can put
other information in the file if you use other kinds of section names.

These are the options:

Serve static files
------------------

::

  file_path = path
  max-age = seconds

The max-age argument is optional.

You can also use just ``single_file = path`` to serve just a single
file at the location

Filtering static files
----------------------

::

  filtered_file_path = path
  simple_html_parse = true
  filter_files = *.txt
  max-age = seconds
  jinja_template = path
  jinja_root_path = path
  # or:
  filter = python.module.filter_func
  option NAME = VALUE

Like serving static files, but the content of files can be filtered.

If ``simple_html_parse`` is true, then HTML files will be parsed into
a simple structure (described in olpcserver.htmlpage).

By default just html files are filtered; you can give a set of
wildcards to specify which pages should be filtered.  Separate
different patterns with spaces.

The filtering can be done by a `Jinja <http://jinja.pocoo.org/>`_
template, or with a filter function.  In either case any keys like
``option NAME = VALUE`` will be passed through.  In Jinja templates
you get the variables:

* environ (WSGI environment)
* headers (List of headers that you can modify)
* path (full file path)
* page (if using simple_html_parse, the page object)

For the filter function, it should look like::

  def filter_func(environ, headers, path, page, **options):
      return modified_string

FIXME: probably it should be possible to add extra Python functions or
pre-load things in the Jinja template.

Serve a WSGI application
------------------------

::

  application = python.module.SomeClass
  ... arguments ...

This creates a WSGI application with
``SomeClass(config_parser_instance, '/path', **arguments)`` and serves
content from that.

Serve from a subprocess
-----------------------

::

  subprocess = /path/to/some/script __PATH__ __PORT__
  cwd = /path/
  environ KEY = VALUE
  clean_environ = true
  idle_shutdown = seconds
  port = 9000


When a request comes to this path, the script is called which should
start up a server.

The internal port in this example is 9000; if not given it will be
automatically determined (by opening up ports until one works).  The
string __PORT__ will be replaced with this port.  __PATH__ will be
replaced with the mount path.  You do not need to use __PATH__;
incoming requests will have the header X-Script-Name, which can be
used to dynamically determine what the path was.

You can control the current working directory that the script is run
in with cwd.  ``environ KEY = VALUE`` settings can be used to control
the environment.  If you use ``clean_environ = true`` then you will be
given a bare environment (otherwise the environment will be inherited
with these overrides).

This server will only be started up when a request first comes in.  If
it isn't accessed for a while it will be shut down (after
idle_shutdown seconds).

FIXME: named subprocesses might be nice, so that multiple paths could
be handled by the same subprocess.

FIXME: it would be nice to support SCGI with named sockets, or even
HTTP with named sockets.

FIXME: there should be a way to serve directly from an activity.  But
how?  Activities come and go.  Listen for dbus messages asking that an
activity get requests?  Probably this config file only applies to
built-in content.
"""

import os
from ConfigParser import ConfigParser
from olpcserver.mapper import MapperApp
from olpcserver.static import StaticApp, FileApp
from olpcserver.spawn import SubprocessApp
from olpcserver.util import simple_import, add_info_to_exception
from olpcserver.filter import FilterApp

HANDLERS = {}

def load_app(filename):
    filename = os.path.abspath(filename)
    parser = ConfigParser()
    parser.read([filename])
    parser.filename = filename
    parser.defaults()['here'] = os.path.dirname(filename)
    parser.defaults()['__file__'] = filename
    return load_app_from_parser(parser)

def load_app_from_parser(parser):
    mapper = MapperApp()
    for section in parser.sections():
        if section.startswith('exact '):
            path = section[len('exact'):].strip()
            exact = True
        elif section.startswith('/'):
            path = section
            exact = False
        else:
            # Not a path section; ignoring
            continue
        mapper.add_application(path, load_app_from_section(parser, section), exact=exact)
    mapper.resolve()
    return mapper

def load_app_from_section(parser, section):
    path = section
    for handler in HANDLERS:
        if parser.has_option(section, handler):
            return HANDLERS[handler](parser, section)
    raise ValueError(
        "Section [%s] in file %s does not have any known handler"
        % (section, parser.filename))

def load_static_app(parser, section):
    location = parser.get(section, 'file_path')
    if parser.has_option(section, 'max-age'):
        max_age = parser.getint(section, 'max-age')
    else:
        max_age = None
    return StaticApp(location, max_age=max_age)

HANDLERS['file_path'] = load_static_app

def load_single_file(parser, section):
    location = parser.get(section, 'single_file')
    if parser.has_option(section, 'max-age'):
        max_age = parser.getint(section, 'max-age')
    else:
        max_age = None
    return FileApp(location, max_age=max_age)

HANDLERS['single_file'] = load_single_file

def load_wsgi_application(parser, section):
    app_name = parser.get(section, 'application')
    try:
        AppClass = simple_import(app_name)
    except ImportError, e:
        add_info_to_exception(e, 'when loading %r from config file %s [%s]'
                              % (app_name, parser.filename, section))
        raise
    kwargs = {}
    for option in parser.options(section):
        value = parser.get(section, option)
        if option == 'application' or option is parser.defaults().get(option):
            continue
        kwargs[option] = value
    return AppClass(parser, section, **kwargs)
    
HANDLERS['application'] = load_wsgi_application

def load_subprocess(parser, section):
    script = parser.get(section, 'subprocess')
    script = script.replace('__PATH__', section)
    if parser.has_option(section, 'clean_environ'):
        clean_environ = parser.getboolean(section, 'clean_environ')
    else:
        clean_environ = False
    if clean_environ:
        env = {}
    else:
        env = os.environ.copy()
    for option in parser.options(section):
        if option.startswith('environ '):
            name = option[len('environ'):].strip()
            env[name] = parser.get(section, option)
    if parser.has_option(section, 'port'):
        port = parser.getint(section, 'port')
    else:
        port = None
    if parser.has_option(section, 'idle_shutdown'):
        idle_shutdown = parser.getint(section, 'idle_shutdown')
    else:
        idle_shutdown = None
    if parser.has_option(section, 'cwd'):
        cwd = parser.get(section, 'cwd')
    else:
        cwd = None
    return SubprocessApp(script,
                         cwd=cwd,
                         environ=env,
                         port=port,
                         idle_shutdown=idle_shutdown)

HANDLERS['subprocess'] = load_subprocess

def load_filtered_files(parser, section):
    path = parser.get(section, 'filtered_file_path')
    if parser.has_option(section, 'simple_html_parse'):
        simple_html_parse = parser.getboolean(section, 'simple_html_parse')
    else:
        simple_html_parse = False
    if parser.has_option(section, 'filter_files'):
        filter_files = parse_filter_files(parser.get(section, 'filter_files'))
    else:
        filter_files = FILTER_HTML_FILES
    if parser.has_option(section, 'max-age'):
        max_age = parser.getint(section, 'max-age')
    else:
        max_age = None
    options = {}
    if parser.has_option(section, 'jinja_template'):
        options['jinja_template'] = parser.get(section, 'jinja_template')
        from olpcserver.jinjafilter import jinja_filter
        filter = jinja_filter
    elif parser.has_option(section, 'filter'):
        name = parser.get(section, 'filter')
        try:
            filter = simple_import(name)
        except ImportError, e:
            add_info_to_exception(e, 'when loading %r from config file %s [%s]'
                                  % (name, parser.filename, section))
    else:
        raise ValueError("No jinja_template or filter option in file %s, section [%s]"
                         % (parser.filename, section))
    for option in parser.options(section):
        if option.startswith('option '):
            name = option[len('option '):].strip()
            options[name] = parser.get(section, optin)
    return FilterApp(path, simple_html_parse=simple_html_parse,
                     filter_files=filter_files,
                     max_age=max_age,
                     filter=filter, options=options)
            

HANDLERS['filtered_file_path'] = load_filtered_files

def parse_filter_files(options):
    import fnmatch
    import re
    options = options.split()
    regex_parts = []
    for option in options:
        if not option:
            continue
        translated = fnmatch.translate(option)
        assert translated.endswith('$')
        translated = translated[:-1]
        regex_parts.append(translated)
    regex = '(?:%s)$' % ('|'.join(regex_parts))
    return re.compile(regex).match

FILTER_HTML_FILES = lambda x: x.endswith('.html')

