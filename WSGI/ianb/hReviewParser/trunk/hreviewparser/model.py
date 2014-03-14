from lxml import etree
from datetime import datetime, date

class HReview(object):

    el = None
    version = None
    version_el = None
    summary = None
    summary_el = None
    type = None
    type_el = None
    item = None
    item_el = None
    reviewer = None
    reviewer_el = None
    dtreviewed = None
    dtreviewed_el = None
    rating = None
    tags = ()
    permalink = None
    permalink_el = None
    license = None
    license_el = None
    description = None
    description_el = None

    def __init__(self, **kw):
        for name, value in kw.items():
            if not hasattr(self, name):
                raise TypeError(
                    "Unexpected keyword argument %s=%r"
                    % (name, value))
            setattr(self, name, value)
        assert self.item is not None, (
            "You must give an item")

    def __repr__(self):
        v = '<%s %s %s' % (
            self.__class__.__name__,
            _format_id(self),
            repr(self.item)[1:-1])
        for attr in ['version', 'summary', 'type', 'reviewer',
                     'dtreviewed', 'rating', 'permalink', 'license',
                     'description', 'tags']:
            if getattr(self, attr):
                r = repr(getattr(self, attr))
                if len(r) > 15:
                    r = r[:9]+'...'+r[-5:]
                v += ' %s=%s' % (attr, r)
        v += '>'
        return v

    def jsonable(self):
        v = {}
        for plain in ['version', 'summary', 'type', 'permalink', 'license',
                      'description', 'reviewer', 'dtreviewed']:
            if getattr(self, plain) is not None:
                v[plain] = getattr(self, plain)
                if isinstance(v[plain], etree._Element):
                    v[plain] = etree.tostring(v[plain])
                elif isinstance(v[plain], (datetime, date)):
                    v[plain] = format_json_date(v[plain])
        # Reviewer should be here:
        for jsonable in ['rating', 'item']:
            if getattr(self, jsonable) is not None:
                v[jsonable] = getattr(self, jsonable).jsonable()
        if self.tags:
            v['tags'] = [t.jsonable() for t in self.tags]
        return v

class Item(object):

    fn = None
    fn_el = None
    el = None
    urls = ()
    photos = ()

    def __init__(self, fn, **kw):
        self.fn = fn
        for name, value in kw.items():
            if not hasattr(self, name):
                raise TypeError(
                    "Unexpected keyword argument %s=%r"
                    % (name, value))
            setattr(self, name, value)

    def __repr__(self):
        v = '<%s %s %r' % (
            self.__class__.__name__, _format_id(self), self.fn)
        if self.urls:
            v += ' urls=%s' % ', '.join([repr(u) for u in self.urls])
        if self.photos:
            v += ' photos=%r' % ', '.join([repr(p) for p in self.photos])
        v += '>'
        return v

    def jsonable(self):
        v = {'fn': self.fn}
        if self.urls:
            v['urls'] = [u.jsonable() for u in self.urls]
        if self.photos:
            v['photos'] = [p.jsonable() for p in self.photos]
        return v

class URL(object):

    url = None
    url_el = None

    def __init__(self, url, url_el=None):
        self.url = url
        self.url_el = url_el

    def jsonable(self):
        return self.url

    def __str__(self):
        return self.url

class Photo(URL):
    pass
    
class Tag(object):

    el = None
    url = None
    rating = None

    def __init__(self, el, url, rating):
        self.el = el
        self.url = url
        self.rating = rating

    def __repr__(self):
        v = '<%s %s %s' % (
            self.__class__.__name__,
            _format_id(self), self.url)
        if self.rating is not None:
            v += ' %s' % repr(self.rating[1:-1])
        v += '>'
        return v

    def jsonable(self):
        v = {'url': self.url}
        if self.rating:
            d = self.rating.jsonable()
            d['rating'] = d.pop('value')
            v.update(d)
        return v

class Rating(object):

    best = 5
    worst = 1
    el = None

    def __init__(self, value, best=None, worst=None,
                 el=None):
        assert isinstance(value, (int, long, float))
        self.value = value
        if best is not None:
            assert isinstance(best, (int, long, float))
            self.best = best
        if worst is not None:
            assert isinstance(worst, (int, long, float))
            self.worst = worst
        self.el = el

    def __repr__(self):
        v = '<%s %s' % (
            self.__class__.__name__,
            self.value)
        if (self.best != self.__class__.best
            or self.worst != self.__class__.worst):
            v += ' of %s-%s' % (worst, best)
        v += '>'
        return v
    
    def jsonable(self):
        v = {'value': self.value}
        if self.best != self.__class__.best:
            v['best'] = self.best
        if self.worst != self.__class__.worst:
            v['worst'] = self.worst
        return v

def _format_id(obj):
    return hex(abs(id(obj)))[2:]

def format_json_date(dt):
    if getattr(dt, 'ambiguous_day', False):
        return dt.strftime('%Y%m')
    elif not getattr(dt, 'hour', None):
        # Really just a date
        return dt.strftime('%Y%m%d')
    else:
        return dt.strftime('%Y%m%dT%H%M%z')
