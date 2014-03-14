import sys
import os
sys.early_modules = sys.modules.copy()
import optparse
import logging
from olpcserver.server import run_simple
from olpcserver.loadapp import load_app

DESCRIPTION = """\
Runs a very simple front-end server that serves static files and can
proxy requests to other ports/servers.

CONFIG_FILE is an ini config file, as described in olpcserver/loadapp.py
"""

parser = optparse.OptionParser(
    usage='%prog [OPTIONS] CONFIG_FILE',
    description=DESCRIPTION,
    )

parser.add_option(
    '--host',
    dest='host',
    default='localhost',
    help='Host to serve on (typically stay with the default localhost)')
parser.add_option(
    '--port',
    dest='port',
    default='80',
    help='Port to serve on (default 80)')
parser.add_option(
    '--no-threaded',
    dest='no_threaded',
    action='store_true',
    help='Do not use threading in the server')
parser.add_option(
    '--reload',
    dest='reload',
    action='store_true',
    help='Use a reloader which regularly polls files for changes (note this has substantial CPU overhead)')
parser.add_option(
    '--validate-wsgi',
    dest='validate_wsgi',
    action='store_true',
    help='Validate any WSGI responses')
parser.add_option(
    '--logging-config',
    dest='logging_config',
    help='Configuration file for logging (see http://python.org/doc/current/lib/node426.html)')

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)
    if not args:
        print 'You must provide a CONFIG_FILE'
        sys.exit(2)
    config_file = args[0]
    if not os.path.exists(config_file):
        print 'The config file %s does not exist' % config_file
        sys.exit(3)
    app = load_app(config_file)
    if options.validate_wsgi:
        from wsgiref.validate import validator
        app = validator(app)
    host = options.host
    port = int(options.port)
    if options.logging_config:
        logging.fileConfig(options.logging_config)
    else:
        logging.basicConfig()
    run_simple(host, port, app, threaded=not options.no_threaded,
               use_reloader=options.reload)

if __name__ == '__main__':
    main()
    
