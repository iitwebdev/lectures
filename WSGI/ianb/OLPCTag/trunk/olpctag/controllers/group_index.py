from olpctag.lib.base import *

class GroupIndexController(BaseController):
    def index(self):
        assert 0, request.environ.keys()
        c.groups = model.Group.select(orderBy=('name', 'slug'))
        return render_response('group_index.myt')
