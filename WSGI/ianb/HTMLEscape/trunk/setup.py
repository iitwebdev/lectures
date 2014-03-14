try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from distutils.core import Extension

version = '0.1'

htmlmodule = Extension('htmlescape._html',
                       sources = ['htmlescape/_htmlmodule.c'])

setup(name='HTMLEscape',
      version=version,
      description="C implementation of HTML escaping function (like cgi.escape)",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='html web cgi',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=["htmlescape"],
      zip_safe=True,
      ext_modules=[htmlmodule],
      )
