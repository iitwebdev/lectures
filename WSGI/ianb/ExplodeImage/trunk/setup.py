from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='ExplodeImage',
      version=version,
      description="",
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
          #'PIL',
          'CmdUtils',
      ],
      entry_points="""
      [console_scripts]
      explodeimage = explodeimage.command:main
      """,
      )
