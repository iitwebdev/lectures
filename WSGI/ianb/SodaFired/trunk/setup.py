from setuptools import setup, find_packages
import sys, os

version = ''

setup(name='SodaFired',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      zip_safe=False,
      install_requires=[
        'PoorMan',
        'Cheetah>=2.0rc',
      ],
      entry_points="""
      [paste.app_factory]
      main = sodafired.web:project.paste_deploy_app
      """,
      )
      
