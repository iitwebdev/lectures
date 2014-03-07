#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
http://maluke.com/old/webdev
"""
import cgi


def hello_app(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    yield "Hello, "
    form = cgi.FieldStorage(environ=environ)
    name = form.getfirst('name', 'stranger')
    yield name


from paste.httpserver import serve
serve(hello_app)
