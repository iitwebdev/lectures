HTML & CSS
==========
[bootstrap](http://getbootstrap.com/components/)

[kube](http://imperavi.com/kube/typography/)

[lesscss](http://lesscss.org/)

[lesscss](http://lesscss.ru/)

[sass](http://sass-lang.com/)

[БЭМ](http://ru.bem.info/)

[haml](http://haml.info/)

[haml-jinja](https://github.com/Pitmairen/hamlish-jinja)

[Jade для python](https://github.com/SyrusAkbary/pyjade)


Синхронный Веб (request&response)
=================================
CGI и WSGI
==========

[Пример CGI скриптов на C++](http://www.tutorialspoint.com/cplusplus/cpp_web_programming.htm "Title")

Для работы нужно поставить библиотеку cgi:

    sudo apt-get install libcgicc5-dev


[Пример CGI скриптов на Python](http://www.tutorialspoint.com/python/python_cgi_programming.htm "Title")

Запуск локального web сервера:


    python -m CGIHTTPServer
    или
    python cgiserver.py

 [Web в python](http://docs.python.org/2/howto/webservers.html)
| [FastCGI](http://flask.pocoo.org/docs/deploying/fastcgi/)

WSGI
----

[Ian Bicking examples](http://svn.colorstudy.com/home/ianb/)

![ScreenShot](https://raw.github.com/iitwebdev/lectures/master/WSGI/ianb/wsgi-tutorial/diagram.png)

[WSGI](http://wsgi.readthedocs.org/en/latest/)

[Примеры как запустить WSGI приложение](http://flask.pocoo.org/docs/deploying/wsgi-standalone/)

[PEP 333](http://legacy.python.org/dev/peps/pep-0333/)

[WSGI middleware example](http://ivory.idyll.org/articles/wsgi-intro/what-is-wsgi.html)

[Getting Started with WSGI](http://lucumr.pocoo.org/2007/5/21/getting-started-with-wsgi/)

[WSGI tutorial](http://webpython.codepoint.net/wsgi_tutorial)

[WSGI citforum](http://citforum.ru/programming/python/wsgi/):

WSGI - стандарт обмена данными между веб-сервером (backend) и веб-приложением (frontend). Под это определение попадают многие вещи, тот же самый CGI.

```python
def app(environ, start_response):
    start_response('200 OK', [('Content-type', 'text/plain')])
    return ['Hello here']
```
        
приложение принимает в качестве аргументов словарь переменных окружения (**environ**) и исполняемый объект выполнения запроса (**start_response**). Далее, посылаем начало ответа серверу и возвращаем сам ответ в виде итератора (в данном случае - в виде обычного списка).

[Python: Веб-разработка без фреймворков](http://maluke.com/old/webdev):

Справедливость ради, стоит упомянуть, что некоторые фреймворки также используют middleware. Например, существует Django middleware, которое, естественно, работает только в своей песочнице и потому для всех остальных бесполезно.

[WSGI middlewares](http://wsgi.readthedocs.org/en/latest/libraries.html)

[A Do-It-Yourself Framework](http://pythonpaste.org/do-it-yourself-framework.html)

[Another Do-It-Yourself Framework](http://webob.readthedocs.org/en/latest/do-it-yourself.html)

[WSGI tutorial](http://archimedeanco.com/wsgi-tutorial/#)

```python
    class Filter(object):
        def __init__(self, application):
            self.application = application
            
        def __call__(self, environ, start_response):
            # Do something here to modify request
            pass
            
            # Call the wrapped application
            app_iter = self.application(environ, 
                                        self._sr_callback(start_response))
            
            # Do something to modify the response body
            pass
            
            # Return modified response
            return app_iter
            
        def _sr_callback(self, start_response):
            def callback(status, headers, exc_info=None):
                # Do something to modify the response status or headers
                pass
            
                # Call upstream start_response
                start_response(status, headers, exc_info)
            return callback
```
            
Шаблоны
=======

[Jinja](http://jinja.pocoo.org/)

[Jinja Flask example](http://www.realpython.com/blog/python/primer-on-jinja-templating/)

[Chameleon](http://chameleon.readthedocs.org/en/latest//)

[Mako](http://www.makotemplates.org/)


Модели
======

[psycopg2](http://pythonhosted.org//psycopg2/)

[psycopg2](http://initd.org/psycopg/)


[sqlite3](http://docs.python.org/2/library/sqlite3.html)

[sqlite3](http://zetcode.com/db/sqlitepythontutorial/)

[sqlite](http://www.tutorialspoint.com/sqlite/sqlite_python.htm)

[SQLAlchemy](http://www.sqlalchemy.org/)

[ZODB](http://www.zodb.org/en/latest/)

[Redis](http://redis.io/)

[memcached](http://memcached.org/)

[mongodb](https://www.mongodb.org/)

[couchdb](http://couchdb.apache.org/)

Тесты
=====

[nose](https://nose.readthedocs.org/en/latest/)

[selenium](http://docs.seleniumhq.org/)

[behave](https://github.com/behave/behave)

[lettuce](https://github.com/gabrielfalcao/lettuce)

[jenkins](http://jenkins-ci.org/)

[buildbot](http://buildbot.net/)

[travis-ci](https://travis-ci.org/)

[StriderCD](http://stridercd.com/)

[Fabric](http://docs.fabfile.org/en/1.8/)

[Docker](https://www.docker.io/)

[Vagrant](http://www.vagrantup.com/)

[drone](https://github.com/drone/drone)

Асинхронный Веб
===============

websocket
---------

[RFC6455](http://tools.ietf.org/html/rfc6455)

[gevent](https://bitbucket.org/Jeffrey/gevent-websocket)

[tornado](http://www.tornadoweb.org/en/stable/)

[Twisted](http://twistedmatrix.com/)

[python>=3.4](http://docs.python.org/dev/library/asyncio.html)

tulip

[socketio](http://socket.io/)

AJAX

[go websocket](http://godoc.org/code.google.com/p/go.net/websocket)

[go gorilla websocket](http://www.gorillatoolkit.org/pkg/websocket)

nodejs

Фреймворки
==========

python
------

Pyramid

Flask

ruby
----

Ruby&Rails

Go
--

Revel

Gorilla

Pyramid
=======

WYSIWYG
-------

[TinyMCE4](http://www.tinymce.com/)

[RedactorJS](http://imperavi.com/redactor/)

Filebrowser
-----------

[Elfinder](http://elfinder.org/)

[pyramid_elfinder](https://github.com/uralbash/pyramid_elfinder)


CRUD
----

[pyramid_formalchemy](http://docs.formalchemy.org/pyramid_formalchemy/)

[sacrud](https://github.com/uralbash/sacrud)

email
-----

[pyramid_mailer](http://docs.pylonsproject.org/projects/pyramid_mailer/en/latest/)
