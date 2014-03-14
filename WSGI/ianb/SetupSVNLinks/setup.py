from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='SetupSVNLinks',
      version=version,
      description="Create setuptools/easy_install-compatible links from an svn repo",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='svn setuptools easy_install subversion',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'CmdUtils',
          'Paste',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      setupsvnlinks = setupsvnlinks.command:main
      """,
      )
