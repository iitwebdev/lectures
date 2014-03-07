#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Webob Responce run test example
"""
from webob import Request
from webob.exc import HTTPException, HTTPNotFound


def webob_wrap(func):
    def wrapped(environ, start_response):
        req = Request(environ)
        if req.charset is None:
            req.charset = 'UTF-8'
            print req.user_agent, 'sucks'
        try:
            app = func(req)
        except HTTPException, app:
            pass
        if app is None:
            app = HTTPNotFound()
        return app(environ, start_response)
    return wrapped


from jsmin import jsmin

js_mimetypes = frozenset(['text/javascript', 'application/x-javascript'])


def jsminify_middleware(app):
    @webob_wrap
    def middleware_app(req):
        r = req.get_response(app)
        #if r.content_type in js_mimetypes and r.body:
        r.decode_content()
        r.body = jsmin(r.body)
        if 'gzip' in req.accept_encoding:
            r.encode_content()
        return r
    return middleware_app

import os
from paste.urlparser import StaticURLParser

yui_app = StaticURLParser('yui', os.path.dirname(__file__))
yui_app = jsminify_middleware(yui_app)

from paste.httpserver import serve
serve(yui_app)
