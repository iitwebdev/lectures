#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Webob example
"""
from webob import Request
from webob.exc import HTTPException, HTTPNotFound


def webob_wrap(func):
    def wrapped(environ, start_response):
        req = Request(environ)
        try:
            app = func(req)
        except HTTPException, app:
            pass
        if app is None:
            app = HTTPNotFound()
        return app(environ, start_response)
    return wrapped


@webob_wrap
def forum_app(req):
    peek = req.path_info_peek()
    if not peek:
        return list_topics_app
    elif peek == 'new_topic':
        return new_topic_app
    elif peek.isdigit():
        topic_id = int(req.path_info_pop())
        return ViewTopicApp(topic_id)


from webob import Response
new_topic_app = Response('NEW')
list_topics_app = Response('<br>'.join('<a href="%d">Topic #%d</a>' % (i, i)
                                       for i in range(10)))


def ViewTopicApp(id):
    return Response('VIEW %d' % id)

from paste.httpserver import serve
serve(forum_app)
