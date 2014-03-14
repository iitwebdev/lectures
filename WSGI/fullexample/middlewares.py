#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Custom middlewares
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


class Wrapper:
    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response):
        resp = ''
        for data in self.wrapped_app(environ, start_response):
            resp += data
        return resp