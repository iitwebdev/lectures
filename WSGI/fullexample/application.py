#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
WSGI web app example
"""
from view import (
    calendar_year,
    calendar_month,
)
from basicauth import BasicAuth
from headinject import HeadInject
from urldispatch import URLDispatch
from errorcatcher import ErrorCatcher
from regexdispatch import RegexDispatch
from simpleapp import simple_app, bad_app
from paste.evalexception.middleware import EvalException


# RegExp URL dispatching middleware
year_regex = r'^/cal/(?P<year>\d\d\d\d)/$'
month_regex = r'^/cal/(?P<year>\d\d\d\d)/(?P<month>\d\d)$'
year_app = RegexDispatch([
    (year_regex, calendar_year),
    (month_regex, calendar_month)])

# AUTH middleware
auth_app = BasicAuth(simple_app, {'user': 'secret'})

# URL dispatching middleware
app_list = [('/users', auth_app),
            ('/year', year_app),
            ('/bad', ErrorCatcher(bad_app)),
            ('/bad2', bad_app),
            ('', simple_app),
            ]
dispatch = URLDispatch(app_list)

# ERROR catcher middleware
app = EvalException(dispatch)

# Add js to head. HeadInject middleware.
app = HeadInject(app, '<script type="text/javascript '
                 'src="/foo.js"></script>')

# WSGI SERVER
from paste.httpserver import serve
serve(app)
