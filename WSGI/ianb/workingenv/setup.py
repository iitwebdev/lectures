try:
    from setuptools import setup
    setuptools = True
except ImportError:
    from distutils.core import setup
    setuptools = False
import os

print "Note: You do not need to use setup.py to use workingenv.py; it is a stand-alone script"

README_filename = os.path.join(os.path.dirname(__file__), 'README.txt')
f = open(README_filename)
lines = f.readlines()
f.close()
README = ''.join(lines[2:])

kw = {}

if setuptools:
    kw['entry_points'] = """
    [console_scripts]
    workingenv = workingenv:main
    """
    kw['zip_safe'] = False
else:
    kw['scripts'] = ['workingenv']

setup(
    name="workingenv.py",
    description="Tool to create isolated Python environment",
    long_description=README,
    version='0.6.6',
    py_modules=['workingenv'],
    classifiers=[
      "Development Status :: 5 - Production/Stable",
      "Intended Audience :: Developers",
      "License :: OSI Approved :: MIT License",
      ],
    keywords="setuptools deployment installation distutils",
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    url="http://cheeseshop.python.org/pypi/workingenv.py",
    license="MIT",
    **kw)

