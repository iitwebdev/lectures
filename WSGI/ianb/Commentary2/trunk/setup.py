from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Commentary2',
      version=version,
      description="Comment on web pages",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'FlatAtomPub',
        'TaggerClient',
        'WSGIFilter',
        'Paste',
      ],
      dependency_links=[
        'http://svn.pythonpaste.org/Paste/apps/FlatAtomPub/trunk#egg=FlatAtomPub-dev',
        'https://svn.openplans.org/svn/TaggerClient/trunk#egg=TaggerClient-dev',
        'http://svn.pythonpaste.org/Paste/WSGIFilter/trunk#egg=WSGIFilter-dev',
      ],
      entry_points="""
      [paste.app_factory]
      main = commentary2.wsgiapp:make_app
      """,
      )
