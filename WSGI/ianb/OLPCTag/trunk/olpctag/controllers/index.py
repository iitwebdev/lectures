from olpctag.lib.base import *

class IndexController(BaseController):
    title = 'Tags'
    def index(self):
        c.tags = list(model.Tag.selectBy(groupID=self.group.id).orderBy('name'))
        return render_response('index.myt')
