#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
WSGI error
"""

from paste.evalexception.middleware import EvalException


def error_app(environ, start_response):
    raise ValueError

from paste.httpserver import serve
serve(EvalException(error_app))
