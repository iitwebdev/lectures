from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='OLPCProxy',
      version=version,
      description="Prototype/demo proxy for OLPC bundle idea",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'PasteDeploy',
          'WSGIProxy',
          'WSGIFilter',
          'lxml',
          'PageCollector',
          'hReviewParser',
      ],
      entry_points="""
      [paste.app_factory]
      main = olpcproxy.wsgiapp:make_app
      """,
      )
