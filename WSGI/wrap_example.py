#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Wrapp many WSGI app
"""


class UpperWare:
    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response):
        resp = ''
        for data in self.wrapped_app(environ, start_response):
            resp += data
        return resp.upper()


class FooWareEach:
    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response):
        resp = ''
        for data in self.wrapped_app(environ, start_response):
            resp += 'foo ' + data
        return resp


class FooWare:
    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response):
        resp = ''
        for data in self.wrapped_app(environ, start_response):
            resp += data
        return 'foo ' + resp


def simple_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world!\n']

from paste.httpserver import serve
serve(FooWare(UpperWare(simple_app)))
