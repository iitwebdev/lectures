import os
from setuptools import find_packages
from paste.util.import_string import import_module
from routes.base import Mapper

def package_regexes(package, exclude=(),
                    regex_suffix=r'/[a-zA-Z]\w*'):
    if isinstance(package, basestring):
        package = import_module(package)
    base = os.path.dirname(package.__file__)
    base = base.replace(os.path.sep, '/')
    packages = find_packages(base, exclude)
    regexes = []
    for pkg in packages:
        regexes.append(pkg.replace('.', '/') + regex_suffix)
    return regexes

class ResolvingMapper(Mapper):

    def __init__(self, package):
        if not isinstance(package, basestring):
            package = package.__name__
        self._package_regexes = package_regexes(package)
    
    def match(self, url):
        if not self._created_args:
            self.create_regs(self._package_regexes)
        return super(Mapper, self).match(url)

    def resolve(self, url):
        pass
    
