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


class YuiLinkGen(object):
    """
    Create a component that generates links to YUI scripts.

        Constructor arguments:

            ``prefix``      Specifies prefix for the generated URIs (location of the YUI files)
            ``debug``       (False by default) Use debug versions of the scripts
            ``minify``      (False by default) Use minified versions of the scripts (debug flag takes precedence)
    """

    js_link_template = '<script type="text/javascript" src="%(prefix)s/%(name)s/%(name)s%(suffix)s.js"></script>'

    def __init__(self, prefix, debug=False, minify=False):
        self.debug = debug
        self.minify = minify
        self.prefix = prefix

        if debug:
            self.suffix = '-debug'
        elif minify:
            self.suffix = '-min'
        else:
            self.suffix = ''

    def js_links(self, names):
        """
        Takes a list of script names (for ex. ['cookie', 'history']) and returns HTML to include in your page.
        """
        links = []
        subst = {'prefix': self.prefix, 'suffix': self.suffix}
        for name in names:
            subst['name'] = name
            links.append(self.js_link_template % subst)
        return '\n'.join(links)

import os
from paste.urlparser import StaticURLParser

yui_app = StaticURLParser('yui', os.path.dirname(__file__))
yui_app = jsminify_middleware(yui_app)


class App(object):
    def __init__(self, yui):
        self.yui = yui

    @webob_wrap
    def __call__(self, req):
        names = [name for name in req.path_info.split('/') if name]
        links = self.yui.js_links(names)

yui = YuiLinkGen('http://static.website.com/scripts/yui', minify=True)
application = App(yui)
from paste.httpserver import serve
serve(application)
