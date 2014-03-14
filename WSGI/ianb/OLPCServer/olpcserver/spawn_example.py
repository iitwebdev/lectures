"""
Example application for a spawned server
"""

import sys
import os
import time
from olpcserver.server import run_simple

started_time = time.time()
last_request = None
counts = 0

def escape(s, quote=None):
    """Replace special characters '&', '<' and '>' by SGML entities."""
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

def example_application(environ, start_response):
    global last_request
    global counts
    counts += 1
    body = '''
    <html>
    <head><title>Example Application</title>
    <style type="text/css">
      li.no-file {
        color: #777;
      }
      li.so-file {
        color: #77a;
      }
    </style>
    <body>
    <h1>Example Application</h1>
    '''
    body += 'Start time = %s sec <br>\n' % started_time
    body += 'Running time = %s sec <br>\n' % (time.time() - started_time)
    if last_request:
        body += 'Since last request = %s sec <br>\n' % (
            time.time() - last_request)
    else:
        body += 'First request <br>\n'
    last_request = time.time()
    body += 'Hits: %s <br>\n' % counts
    body += 'PID: %s <br>\n' % os.getpid()
    body += '<h2>Environ:</h2>\n'
    body += '<table border=1>\n'
    for key in sorted(environ):
        value = environ[key]
        if key.upper() != key:
            value = repr(value)
        body += '<tr><td>%s</td><td>%s</td></tr>\n' % (
            key, escape(value, 1))
    body += '</table>'
    body += '<h2>sys.modules</h2>\n'
    early_modules = getattr(sys, 'early_modules', {})
    new_modules = {}
    for name in sys.modules:
        if name not in early_modules:
            new_modules[name] = sys.modules[name]
    body += format_modules(new_modules)
    if early_modules:
        body += '<h2>Early-loaded modules</h2>\n'
        body += format_modules(early_modules)
    body += '</body></html>'
    start_response('200 OK', [
        ('Content-Type', 'text/html'),
        ('Content-Length', str(len(body)))])
    return [body]

def format_modules(modules):
    body = '<ul>'
    for name in sorted(modules):
        if modules[name] is None:
            continue
        filename = getattr(modules[name], '__file__', '(unknown)')
        if filename == '(unknown)':
            classname = 'no-file'
        elif filename.endswith('.so'):
            classname = 'so-file'
        else:
            classname = ''
        body += '<li class="%s"><code>%s</code> in %s</li>\n' % (
            classname, name, filename)
    body += '</ul>\n'
    return body

def make_app(parser, section, **kw):
    def app(environ, start_response):
        environ.update(kw)
        environ['olpcserver.example_parser'] = (parser, section)
        return example_application(environ, start_response)
    return app

import atexit
def waitstop():
    import sys
    print 'Stopping at', time.time(), 'sleeping 20 seconds...'
    for i in range(20):
        print i,
        sys.stdout.flush()
        time.sleep(1)
    print 'done.'
atexit.register(waitstop)

def _turn_sigterm_into_systemexit():
    """
    Attempts to turn a SIGTERM exception into a SystemExit exception.
    """
    try:
        import signal
    except ImportError:
        return
    def handle_term(signo, frame):
        raise SystemExit
    signal.signal(signal.SIGTERM, handle_term)

if __name__ == '__main__':
    import logging
    if not sys.argv[1:]:
        print 'Usage: %s PORT' % (os.path.basename(sys.argv[0]))
        sys.exit(2)
    port = int(sys.argv[1])
    # Note: you might want threaded=False:
    print 'started server at', time.time()
    _turn_sigterm_into_systemexit()
    run_simple('localhost', port, example_application, threaded=True)
    
