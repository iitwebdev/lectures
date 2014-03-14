from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='OLPCServer',
      version=version,
      description="Server for the XO laptop",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'wsgiref',
      ],
      entry_points="""
      [console_scripts]
      olpcserver = olpcserver.command:main
      """,
      )
