"""
::

  >>> import sys
  >>> sys.path_hooks.append(HTTPImporter)
  >>> sys.path.insert(0, 'http://svn.colorstudy.com/home/ianb/recipes')
  >>> import html
  >>> html.__file__
  http://svn.colorstudy.com/home/ianb/recipes/html.py

"""

import sys
import imp
import urllib2

class HTTPImporter(object):

    def __init__(self, url):
        if (not url.startswith('http://')
            and not url.startswith('https://')):
            raise ImportError
        if not url.endswith('/'):
            url += '/'
        self.url = url

    def find_module(self, fullname, path=None):
        # @@: Should pay attention to path
        result = self._get_module(fullname)
        if result is None:
            return result
        return ModuleLoader(fullname, *result)

    def _get_module(self, fullname):
        path = fullname.replace('.', '/')
        path = self.url + path
        options = [
            (path + '.py', False),
            (path + '/__init__.py', True)]
        for option, ispkg in options:
            try:
                f = urllib2.urlopen(option)
                code = f.read()
                f.close()
                return option, ispkg, code
            except urllib2.HTTPError:
                pass
        return None

class ModuleLoader(object):

    def __init__(self, fullname, url, ispkg, code):
        self.fullname = fullname
        self.url = url
        self.ispkg = ispkg
        self.code = code
        
    def load_module(self, fullname):
        assert fullname == self.fullname
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = self.url
        mod.__loader__ = self
        if self.ispkg:
            mod.__path__ = []
        exec self.code in mod.__dict__
        return mod

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
