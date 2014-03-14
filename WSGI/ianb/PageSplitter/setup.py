from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='PageSplitter',
      version=version,
      description="Split HTML pages into smaller chunks",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='html lxml olpc ebook',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'CmdUtils',
          'lxml==html,>=1.3.beta',
      ],
      dependency_links=[
          'http://codespeak.net/svn/lxml/branch/html#egg=lxml-html',
      ],
      entry_points="""
      [console_scripts]
      pagesplitter = pagesplitter.command:main
      """,
      )
