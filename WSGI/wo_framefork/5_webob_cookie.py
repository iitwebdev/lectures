#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Webob Responce example
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


from webob import Response


@webob_wrap
def hello_app_cookie(req):
    r = Response(charset='UTF-8')
    if 'name' in req.params:
        name = req.params['name']
        r.set_cookie('name', name)
    elif 'name' in req.cookies:
        name = req.cookies['name']
        #r.delete_cookie('name')
    else:
        return form_app
    r.unicode_body = u'Hello, %s!' % name

    r.conditional_response = True
    r.md5_etag()
    return r

form_app = Response('<form method=POST><input name=name><input type=submit>')

#application = hello_app_cookie
from paste.httpserver import serve
serve(hello_app_cookie)
