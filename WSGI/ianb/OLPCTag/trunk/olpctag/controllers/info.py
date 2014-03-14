from olpctag.lib.base import *

class InfoController(BaseController):
    def index(self):
        uri = request.urlvars['uri']
        c.page = model.Page.byUri(uri)
        return render_response('info.myt')
