from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(
    name='hReviewCollector',
    version="0.1",
    description="Collect documents from hReview annotations",
    author="Ian Bicking",
    author_email="ianb@colorstudy.com",
    #url="",
    install_requires=[
      "Pylons>=0.9.4",
      'httplib2',
      "hReviewParser",
      'PageCollector',
      'OHM',
      ],
    dependency_links=[
      "http://svn.colorstudy.com/home/ianb/hReviewParser/trunk#egg=hReviewParser-dev",
    ],
    packages=find_packages(),
    include_package_data=True,
    test_suite = 'nose.collector',
    package_data={'hreviewcollector': ['i18n/*/LC_MESSAGES/*.mo']},
    entry_points="""
    [paste.app_factory]
    main=hreviewcollector:make_app
    [paste.app_install]
    main=pylons.util:PylonsInstaller
    """,
)
