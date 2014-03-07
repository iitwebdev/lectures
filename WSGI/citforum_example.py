#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
WSGI example
http://citforum.ru/programming/python/wsgi/
"""
from wsgiref import simple_server


def app(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['Hello here']

server = simple_server.WSGIServer(
    ('', 8080),
    simple_server.WSGIRequestHandler,
)
server.set_app(app)
server.serve_forever()
