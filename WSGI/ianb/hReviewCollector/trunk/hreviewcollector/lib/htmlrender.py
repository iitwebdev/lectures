from hreviewparser import model
from webhelpers.util import html_escape
import re
from hreviewcollector.collector import http
from hreviewcollector.models import Bundle
from pylons import c

_registry = {}

def html(obj, **kw):
    if type(obj) not in _registry:
        raise TypeError(
            "There's no renderer registered for the type %r (when rendering %r)" % (type(obj), obj))
    #print 'Rendering %r with %s' % (
    #    obj, _registry[type(obj)])
    return _registry[type(obj)](obj, **kw)

def renderer(obj_type):
    if not isinstance(obj_type, tuple):
        obj_type = (obj_type,)
    def decorator(func):
        for o_type in obj_type:
            _registry[o_type] = func
        return func
    return decorator

_url_titles = {}
_title_re = re.compile(r'<title>(.*?)</title>', re.I|re.S)

def get_title(url):
    if url not in _url_titles:
        resp, content = http.request(url, 'GET')
        match = _title_re.search(content)
        if not match:
            title = url
        else:
            title = match.group(1)
        _url_titles[url] = title
    return _url_titles[url]

############################################################
## Renderers
############################################################

@renderer(model.HReview)
def render_hreview(hreview):
    content = []
    content.append(html(hreview.item))
    if hreview.rating:
        content.append('Rating: %s<br>' % html(hreview.rating))
    if hreview.tags:
        content.append('<div class="hreview-tags">Tags: ')
        for tag in hreview.tags:
            content.append(html(tag))
        content.append('</div>')
    if hreview.description:
        # @@ Should clean HTML/Javascript here:
        content.append(hreview.description)
    return '<div class="hreview">%s</div>' % ''.join(content)

@renderer(model.Tag)
def render_tag(tag):
    title = html_escape(get_title(tag.url))
    if tag.rating:
        title += ' ' + html(tag.rating)
    return '<a rel="tag" href="%s">%s</a>' % (html_escape(tag.url), title)

@renderer(model.Rating)
def render_rating(rating):
    if rating.value >= rating.best:
        extra_class = "best-rating"
    elif rating.value >= rating.best - 1:
        extra_class = "good-rating"
    elif rating.value <= rating.worst:
        extra_class = "worst-rating"
    elif rating.value <= rating.worst + 1:
        extra_class = "bad-rating"
    else:
        extra_class = "middle-rating"
    if rating.best != 5 or rating.worst != 1:
        if rating.worst != 1:
            content = '<span class="value">%s</span> on scale of <span class="worst">%s</span>-<span class="best">%s</span>' % (
                rating.value, rating.worst, rating.best)
        else:
            content = '<span class="value">%s</span> out of <span class="best">%s</span>' % (
                rating.value, rating.best)
        return '<span class="rating %s">%s</span>' % (extra_class, content)
    else:
        return '<span class="rating %s">%s</span>' % (extra_class, rating.value)

@renderer(model.Item)
def render_item(item):
    title = item.fn
    if item.urls:
        title = '<a href="%s" class="url fn">%s</a>' % (html(item.urls[0]), title)
    else:
        title = '<span class="fn">%s</span>' % title
    extra_title = []
    if len(item.urls) > 1:
        for url in item.urls[1:]:
            extra_title.append(
                '<a href="%s" class="url">%s</a>' % (
                html(url), html_escape(get_title(url))))
    if extra_title:
        title += ' ' + ' '.join(extra_title)
    # @@: Should do something with photos here
    content = title
    return '<div class="item">%s</div>' % content

@renderer((model.URL, model.Photo))
def render_url(url):
    return html(url.url)

@renderer(type(None))
def render_none(none):
    return ''

@renderer((str, unicode))
def render_string(s):
    return html_escape(s)

@renderer(Bundle)
def render_bundle(bundle):
    link = c.url(bundle.name, '')
    return '<div class="bundle"><a href="%s">%s</a></div>' % (
        link, bundle.title)
