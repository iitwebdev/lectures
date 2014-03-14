from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='PageCollector',
      version=version,
      description="Fetches HTML pages and strips out content",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='scraper html web',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'lxml',
        'WSGIFilter',
        'httplib2',
      ],
      entry_points="""
      [console_scripts]
      pagecollector = pagecollector.command:main
      """,
      )
