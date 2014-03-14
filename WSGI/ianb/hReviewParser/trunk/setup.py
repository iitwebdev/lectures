from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='hReviewParser',
      version=version,
      description="Parser the hReview microformat",
      long_description="""\
""",
      #classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='microformat parser',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      #url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'lxml',
        'python-dateutil',
        'simplejson',
      ],
      #entry_points="""
      #""",
      )
