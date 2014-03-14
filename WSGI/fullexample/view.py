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
import calendar
from caller import wsgify
from models import fraimworks
from jinja2 import (
    Template,
    Environment,
    #PackageLoader,
    FileSystemLoader
)

#env = Environment(loader=PackageLoader('fullexample', 'templates'))
env = Environment(loader=FileSystemLoader('templates'))


@wsgify
def calendar_year(request, year):
    request.response.set_header('content-type', 'text/plain')
    cal = calendar.calendar(int(year))
    return str(cal)


@wsgify
def calendar_month(request, year, month):
    request.response.set_header('content-type', 'text/plain')
    cal = calendar.month(int(year), int(month))
    return str(cal)


@wsgify
def index(request):
    with open('templates/index.html', 'r') as template_file:
        template = template_file.read()
    t = Template(str(template))
    response = t.render(name="WSGI examples")
    return response


@wsgify
def models_view(request):
    template = env.get_template('fraimworks_list.html')
    response = template.render(fraimworks=fraimworks, name="Fraimworks list")
    return response
