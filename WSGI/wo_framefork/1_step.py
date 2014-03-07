#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
http://maluke.com/old/webdev
"""
from paste.urlmap import URLMap
from paste.fileapp import FileApp

root_app = URLMap()
root_app['/static'] = FileApp('/var/www/static/')

from paste.auth.digest import digest_password, AuthDigestHandler


def private_app(environ, start_response):
    remote_user = environ['REMOTE_USER']
    app = FileApp('/home/%s/htdocs/' % remote_user)
    return app(environ, start_response)


def authfunc(environ, realm, username):
    return digest_password(realm, username, username)  # password == username


private_wrapped = AuthDigestHandler(private_app, "Private area", authfunc)
root_app['/private'] = private_wrapped

from paste.httpserver import serve
serve(root_app)
