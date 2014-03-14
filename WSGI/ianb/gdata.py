"""
A GData parser

GData:
* http://code.google.com/apis/gdata/
* http://code.google.com/apis/gdata/reference.html

Includes an extension:

``?rel-NAME=HREF`` for searching for ``<link rel="NAME" href="HREF">``
"""
# normalize handling of "or"

from dateutil.parser import parse as parse_date
try:
    from taggerindex import rdf
except ImportError:
    # TaggerStore is an optional requirement
    # maybe we should make the query output pluggable
    rdf = None
from utils import to_uri, to_urn
import urllib
from cStringIO import StringIO
import re
import urllib
import itertools
from lxml import etree
from taggerclient.atom import tostring

__all__ = ['parse_gdata', 'GDataQuery']

_scheme_re = re.compile(r'[{](.*?)[}]')

_recode = re.compile(r'[{](?P<scheme>.*?)[}][<](?P<uri>.*?)[>]')

el_string_content = etree.XPath("string()")

def parse_gdata(req):
    """
    Parses a url segment, returning the query.  The portion of
    the path parsed is in the PATH_INFO (request.path_info)
    """
    args = {}
    for var in ['q', 'author', 'alt']:
        args[var] = req.params.get(var)
    for var in ['start-index', 'max-results']:
        if req.params.get(var):
            value = int(req.params[var])
            args[var.replace('-', '_')] = value
    for date_prefix in ['updated', 'published']:
        min_var = req.params.get('%s-min' % date_prefix)
        max_var = req.params.get('%s-max' % date_prefix)
        if min_var or max_var:
            args[date_prefix] = (_parse_date(min_var), _parse_date(max_var))
    path_info = requote_pathinfo(req.path_info)
    category_query = parse_pathinfo(path_info)
    entry_id = parse_entry_id(path_info)
    rels = {}
    for name, value in req.params.items():
        if name.startswith('rel-'):
            name = name[4:]
            ## FIXME: watch for clobbering?
            ## Would multiple values mean OR or AND?
            rels[name] = value
    if rels:
        args['rels'] = rels
    return GDataQuery(
        entry_id=entry_id, category_query=category_query, **args)

def requote_pathinfo(path_info):
    """To preserve urls that wsgi has unquoted, we requote path_info
    and unquote after splitting the pathinfo on slashes"""
    uris = _recode.findall(path_info)
    new_pathinfo = str(path_info)
    uris = tuple(itertools.chain(*uris))
    for uri in set(uris):
        new_pathinfo=new_pathinfo.replace(uri, urllib.quote(uri, safe=''))
    return new_pathinfo

def parse_entry_id(path_info):
    entry_id = None
    parts = [p for p in path_info.split('/') if p]
    if parts and parts[0] != '-':
        # FIXME: I'm not sure if I should look for more segments?
        # Does an entry ID mean this isn't really a query at all?
        entry_id = parts[0]
    return entry_id

def parse_pathinfo(path_info):
    parts = [p for p in path_info.split('/') if p]
    category_query = None
    if '-' in parts:
        categories = parts[parts.index('-')+1:]
        if categories:
            if len(categories) == 1:
                category_query = _parse_segment(categories[0])
            else:
                category_query = AND([
                    _parse_segment(c) for c in categories])
    return category_query

def _parse_segment(seg):
    if '|' in seg:
        return OR([
            _parse_segment(s) for s in seg.split('|')
            if s])
    if seg.startswith('-'):
        return NOT(_parse_segment(seg[1:]))
    match = _scheme_re.search(seg)
    if match:
        return Category(to_uri(seg[match.end():]), to_uri(match.group(1)))
    else:
        return Category(seg)

def _parse_date(value):
    if not value:
        return None
    return parse_date(value)

def _str_date(d):
    return d.strftime('%Y-%m-%dT%H:%M:%S')
        
class GDataQuery(object):
    def __init__(self, q=None, category_query=None, author=None,
                 alt=None, rels=None, updated=None, published=None,
                 start_index=1, max_results=None, entry_id=None):
        self.q = q
        self.category_query = category_query
        self.author = author
        self.alt = alt
        self.rels = rels
        self.updated = updated or (None, None)
        self.published = published or (None, None)
        # start_index is 1 indexed!
        self.start_index = start_index
        self.max_results = max_results
        self.entry_id = entry_id

    def __str__(self):
        qs = {}
        for var in ['q', 'author', 'alt', 'max_results']:
            value = getattr(self, var, None)
            var = var.replace('_', '-')
            if value is not None:
                qs[var] = str(value)
        if self.start_index and self.start_index != 1:
            qs['start-index'] = str(self.start_index)
        for date_prefix in ['updated', 'published']:
            value = getattr(self, date_prefix, None)
            if not value or value == (None, None):
                continue
            min_date, max_date = value
            if min_date:
                qs['%s-min' % date_prefix] = _str_date(min_date)
            if max_date:
                qs['%s-max' % date_prefix] = _str_date(max_date)
        if self.category_query:
            path = '/-/%s' % self.category_query
        elif self.entry_id:
            path = '/%s' % self.entry_id
        else:
            path = '/'
        path = urllib.quote(path)
        if qs:
            path += '?' + urllib.urlencode(qs)
        return path

    def _sparql(self, template=None):
        if template is None:
            template = rdf.template_query
        return rdf.make_q(self.category_query._pattern, template=template)

    def evaluate(self, entry):
        if self.q:
            content = el_string_content(entry)
            content_lower = content.lower()
            items = self.q.split()
            for item in items:
                if item.lower() == item:
                    if item not in content_lower:
                        return False
                else:
                    if item not in content:
                        return False
        if self.author:
            ok = False
            author = entry.author
            if not author:
                return False
            if author.email and author.email.lower() == self.author.lower():
                ok = True
            if author.name and self.author.lower() in author.name.lower():
                ok = True
            if author.uri and self.author == author.uri:
                ok = True
            if not ok:
                return False
        if self.updated:
            if self.updated[0] and entry.updated and entry.updated < self.updated[0]:
                return False
            if self.updated[1] and entry.updated and entry.updated > self.updated[1]:
                return False
        if self.published:
            if self.published[0] and entry.published and entry.published < self.published[0]:
                return False
            if self.published[1] and entry.published and entry.published > self.published[1]:
                return False
        # entry_id doesn't count
        # start_index and max_results is handled elsewhere
        if self.category_query and not self.category_query.evaluate(entry):
            return False
        if self.rels:
            for rel_type, href in self.rels.items():
                for link in entry.rel_links(rel_type):
                    ## FIXME: relative links?
                    if link.href == link.href:
                        break
                else:
                    return False
        return True

class OP(list):
    operator = "OPERATOR"
    template = "%s"
    def __repr__(self):
        return '%s(%r)' %(self.operator, list(self))
    def _pattern_(self):
        """ generators a sparql pattern for all subpatterns"""
        out = StringIO()
        for seg in self:
            if isinstance(seg, Category):
                print >> out, self.template %seg._pattern
            else:
                print >> out, seg._pattern
        return out.getvalue()
    _pattern = property(_pattern_)

class AND(OP):
    operator = 'AND'
    def __str__(self):
        return '/'.join([str(e) for e in self])

    def evaluate(self, entry):
        for item in self:
            if not item.evaluate(entry):
                return False
        return True

class OR(OP):
    operator = 'OR'
    template = "OPTIONAL{%s}\n"
    def __str__(self):
        return '|'.join([str(e) for e in self])

    def evaluate(self, entry):
        for item in self:
            if item.evaluate(entry):
                return True
        return False

class NOT(object):
    operator = 'NOT'
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return 'NOT(%r)' % self.expr
    def __str__(self):
        return '-%s' % self.expr
    @property
    def _pattern(self):
        return self.expr._negation

    def evaluate(self, entry):
        return not self.expr.evaluate(entry)

class Category(object):

    def __init__(self, term, scheme=None):
        self.term = to_uri(term)
        if scheme:
            scheme = to_uri(scheme)
        self.scheme=scheme

    def __repr__(self):
        if self.scheme is None:
            extra = ''
        else:
            extra = ', scheme=%r' % self.scheme
        return 'Category(%r%s)' % (self.term, extra)

    def __str__(self):
        if self.scheme is None:
            return self.term
        else:
            return '{%s}%s' % (self.scheme, self.term)

    @property
    def _predicate(self):
        """
        determines an appropriate query predicate for matching or
        filtering depending on the category's scheme
        """
        if self.scheme:
            return rdf.scheme_to_pattern_map.get(self.scheme, str(rdf.HAS_SCHEME))
        return rdf.scheme_to_pattern_map.get(str(rdf.LABEL))

    @property
    def _pattern(self):
        return self._predicate %self.term

    @property
    def _negation(self):
        slug = rdf.scheme_to_filter_map.get(str(rdf.LABEL))
        if self.scheme:
            slug = rdf.scheme_to_filter_map.get(self.scheme)
        
        return "FILTER(%s)\n"%(slug %self.term)

    def evaluate(self, entry):
        for category in entry.categories:
            if self.scheme is not None:
                if ((category.scheme != self.scheme)
                    and (category.scheme or self.scheme)):
                    continue
            if category.term == self.term:
                return True
        return False
