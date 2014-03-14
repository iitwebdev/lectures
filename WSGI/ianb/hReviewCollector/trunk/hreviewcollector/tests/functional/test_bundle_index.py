from hreviewcollector.tests import *

class TestBundleIndexController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='bundle_index'))
        # Test response...