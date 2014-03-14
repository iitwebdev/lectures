import os
import sys
from cssselect import css_to_xpath, SelectorSyntaxError, ExpressionError
from webob import Request, Response
from webob import exc
from google.appengine.ext.webapp import template

here = os.path.dirname(__file__)

def application(environ, start_response):
    req = Request(environ, charset='utf8')
    try:
        resp = handle_request(req)
    except exc.HTTPException, resp:
        pass
    return resp(environ, start_response)

def handle_request(req):
    if req.path_info and req.path_info != '/':
        raise exc.HTTPNotFound()
    css = req.GET.get('css')
    if css:
        xpath = error = None
        try:
            xpath = css_to_xpath(css)
            status = 200
        except (SelectorSyntaxError, ExpressionError, AssertionError), e:
            error = str(e)
            status = 400
        except TypeError, e:
            error = 'Internal error: %s' % e
            status = 500
        if req.GET.get('format') == 'html':
            resp = Response(
                template.render(os.path.join(here, 'form.html'),
                                dict(xpath=xpath, error=error, req=req, css=css)),
                status=status)
            if error:
                resp.body += '<!-- %s -->' % (('*'*40+'\n')*100)
            return resp
        else:
            resp = Response(
                xpath or error,
                content_type='text/plain',
                status=status)
            return resp
    
    return Response(template.render(os.path.join(here, 'form.html'),
                                    dict(req=req)))
    
def main():
    import wsgiref.handlers
    wsgiref.handlers.BaseCGIHandler(
        sys.stdin, sys.stdout, sys.stderr, os.environ, 
        multiprocess=False).run(application)

if __name__ == '__main__':
    main()

