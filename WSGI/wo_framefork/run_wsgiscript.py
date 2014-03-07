#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Example reloaded wsgi server
http://maluke.com/old/webdev#запуск_wsgiскриптов_без_apache
"""
import sys
import os
from time import sleep
from traceback import print_exc

from paste.httpserver import serve
from paste.evalexception import EvalException
from paste.debug.prints import PrintDebugMiddleware
from paste import reloader


def run_script(script):
    if not os.path.isfile(script):
        print script, "does not exist"
        sys.exit(1)
    reloader.install()
    reloader.watch_file(script)

    script_locals = {}
    execfile(script, {'__file__': script}, script_locals)
    app = script_locals['application']
    app = EvalException(app)
    app = PrintDebugMiddleware(app)
    serve(app)

if __name__ == '__main__':
    try:
        run_script(sys.argv[1])
    except SystemExit, exc:
        raise exc
    except:
        print_exc()
        print '-' * 20, 'Restarting in 5 secs..', '-' * 20
        sleep(5)
        sys.exit(3)
