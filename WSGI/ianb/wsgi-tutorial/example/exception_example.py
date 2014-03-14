import sys
sys.path.append('/home/ianb/src/colorstudy/wsgi-tutorial/code')

from caller import wsgify

@wsgify
def my_stupid_app(req):
    if req.params.get('name'):
        return 'Hi %s' % name
    else:
        return '''
        What is your name?
        <form action="%s" method="post">
        <input type="text" name="name">
        <input type=submit>
        </form>
        ''' % req.request_url

# Decorator introduction:
#   @wsgify
#   def foo(...)
# same as:
#   def foo(...)
#   foo = wsgify(foo)

if __name__ == '__main__':
    from paste.httpserver import serve
    #serve(my_stupid_app)
    from paste.evalexception import EvalException
    serve(EvalException(my_stupid_app))
    
    
