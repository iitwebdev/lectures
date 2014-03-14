from hreviewcollector.lib.base import *
from hreviewcollector.collector import get_reviews
from pagecollector import ResourceCollection, Page
from cStringIO import StringIO
import time

class IndexController(BaseController):
    title = 'Content Collector'
    def set_urls(self):
        return render_response('index_set_urls.myt')

    def get_urls(self):
        value = self.bundle.urls
        if not value:
            redirect_to(str(c.bundle_url('set_urls')))
        return value

    def set_urls_submit(self):
        urls = request.params['urls'].split()
        self.bundle.urls = urls
        redirect_to(str(c.bundle_url('')))

    def index(self):
        urls = self.get_urls()
        c.hreviews = get_reviews(urls)
        return render_response('index.myt')

    def content(self):
        urls = self.get_urls()
        parts = []
        total_size = 0
        total_urls = 0
        for review in get_reviews(urls):
            if not review.item.urls:
                # We want nothing of this!
                continue
            for url in review.item.urls:
                total_urls += 1
                url = url.url
                page = Page(url)
                page.read_content()
                size = page.size()
                embedded_size = get_embedded_size(page)
                total_size += size + embedded_size
                parts.append((review, Page(url), size, embedded_size))
        c.review_parts = parts
        c.total_size = total_size
        c.total_urls = total_urls
        return render_response('index_content.myt')

    def download(self):
        urls = self.get_urls()
        res = Response()
        res.headers['Content-Disposition'] = 'attachment; filename="content_%s.zip"' % time.strftime('%Y-%m-%d')
        res.headers['Content-type'] = 'application/zip'
        col = ResourceCollection()
        for review in get_reviews(urls):
            for url in review.item.urls:
                url = url.url
                col.add_object(Page(url))
        col.serialize_to_zip(res)
        return res
        
def get_embedded_size(page):
    page.read_content()
    size = 0
    for obj in page.embedded_objects():
        obj.read_content()
        size += obj.size()
    return size
