from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='PoorMan',
      version=version,
      description="PoorMan is a trimmed-down framework",
      long_description="""\
This somewhat experimental web framework is an attempt to make
something small and useful.

It's only for you at this point if you just *love* new frameworks.
""",
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Topic :: Internet :: WWW/HTTP',
          'License :: OSI Approved :: MIT License',
      ],
      keywords='web framework wsgi paste routes',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='http://pythonpaste.org/poorman/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=[
          'Paste',
          'FormEncode',
          'PasteDeploy',
          'PasteScript',
          'Wareweb',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
