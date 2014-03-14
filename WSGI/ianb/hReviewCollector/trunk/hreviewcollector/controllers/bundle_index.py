from hreviewcollector.lib.base import *

class BundleIndexController(BaseController):
    def index(self):
        if request.method == 'POST':
            return self.submit()
        else:
            c.bundles = list(model.Bundle.all_bundles())
            return render_response('bundle_index.myt')

    def submit(self):
        title = request.params['title']
        name = model.Bundle.name_from_title(title)
        if model.Bundle.exists(name):
            self.flash('That bundle already exists!')
            h.redirect_to(c.url(''))
        bundle = model.Bundle(name=name, title=title)
        self.flash('Bundle %s created' % title)
        h.redirect_to(c.url(bundle.name))
        
            
