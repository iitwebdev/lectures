from olpctag.tests import *

class TestBookmarkletController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='bookmarklet'))
        # Test response...