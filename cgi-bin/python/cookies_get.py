#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

# Import modules for CGI handling
from os import environ
import cgi, cgitb


print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head>"
print "<title>Hello - Second CGI Program</title>"
print "</head>"
print "<body>"
if environ.has_key('HTTP_COOKIE'):
   for cookie in split(environ['HTTP_COOKIE'], ';'):
      (key, value ) = split(cookie, '=');
      print "%s: %s" % (key, value)
      print "%(key)s: %(value)s" % {'key': key, 'value': value}
      print "<br/>"
print "</body>"
print "</html>"
