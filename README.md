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

[WSGI](http://wsgi.readthedocs.org/en/latest/)

[Примеры как запустить WSGI приложение](http://flask.pocoo.org/docs/deploying/wsgi-standalone/)

[PEP 333](http://legacy.python.org/dev/peps/pep-0333/)

[WSGI citforum](http://citforum.ru/programming/python/wsgi/):

WSGI - стандарт обмена данными между веб-сервером (backend) и веб-приложением (frontend). Под это определение попадают многие вещи, тот же самый CGI.

    def app(environ, start_response):
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ['Hello here']
        
приложение принимает в качестве аргументов словарь переменных окружения (**environ**) и исполняемый объект выполнения запроса (**start_response**). Далее, посылаем начало ответа серверу и возвращаем сам ответ в виде итератора (в данном случае - в виде обычного списка).

[Python: Веб-разработка без фреймворков](http://maluke.com/old/webdev):

Справедливость ради, стоит упомянуть, что некоторые фреймворки также используют middleware. Например, существует Django middleware, которое, естественно, работает только в своей песочнице и потому для всех остальных бесполезно.

[WSGI middlewares](http://wsgi.readthedocs.org/en/latest/libraries.html)

[A Do-It-Yourself Framework](http://pythonpaste.org/do-it-yourself-framework.html)

[Another Do-It-Yourself Framework](http://webob.readthedocs.org/en/latest/do-it-yourself.html)

[WSGI tutorial](http://archimedeanco.com/wsgi-tutorial/#)


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
