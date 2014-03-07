#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
CGI env
http://www.tutorialspoint.com/python/python_cgi_programming.htm
"""
import os

print "Content-type: text/html\r\n\r\n"
print "<font size=+1>Environment</font><\br>"
for param in os.environ.keys():
    print "<b>%20s</b>: %s<br/>" % (param, os.environ[param])
