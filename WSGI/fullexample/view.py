#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Any views there.
"""
from caller import wsgify
import calendar


@wsgify
def calendar_year(req, year):
    req.response.set_header('content-type', 'text/plain')
    cal = calendar.calendar(int(year))
    return str(cal)


@wsgify
def calendar_month(req, year, month):
    req.response.set_header('content-type', 'text/plain')
    cal = calendar.month(int(year), int(month))
    return str(cal)
