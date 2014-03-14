from olpctag.tests import *

class TestSubmitController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='submit'))
        # Test response...