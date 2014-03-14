from olpctag.lib.base import *

class BookmarkletController(BaseController):
    title = 'Use Bookmarklets'
    def index(self):
        return render_response('bookmarklet.myt')
