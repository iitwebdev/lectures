from olpctag.tests import *

class TestGroupIndexController(TestController):
    def test_index(self):
        response = self.app.get(url_for(controller='group_index'))
        # Test response...