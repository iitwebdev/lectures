from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='DeliveranceStatic',
      version=version,
      description="Render static pages using Deliverance",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='web html template',
      author='Ian Bicking',
      author_email='ianb@colorstudy.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'Deliverance',
      ],
      entry_points="""
      [console_scripts]
      deliv-static = delivstatic.command:main
      """,
      )
      
