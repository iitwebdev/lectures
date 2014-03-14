from lxml import etree
import urlparse
import urllib
import copy
from wsgifilter import fixuplinks
from wsgifilter import htmlserialize
import httplib2
import urlparse
import posixpath
import os
import zipfile
import mimetypes

if not mimetypes.guess_extension('text/javascript'):
    mimetypes.add_type('text/javascript', '.js')
if mimetypes.guess_extension('image/jpeg') == '.jpe':
    # Have to fix up the stupid image/jpeg -> jpe extension:
    db = mimetypes.add_type.im_self
    db.types_map_inv[True]['image/jpeg'].insert(0, '.jpg')

http = httplib2.Http('http-cache')

class ResourceCollection(object):

    def __init__(self):
        self.objects = {}

    @classmethod
    def from_page(cls, url):
        self = cls()
        page = Page(url, type='text/html')
        self.add_object(page)

    def add_object(self, obj, resolve=True, recurse=True):
        if obj.url in self.objects:
            # Throw it away, we don't want it
            return
        if resolve and obj.content is None:
            obj.read_content()
        self.objects[obj.url] = obj
        if recurse:
            for sub_obj in obj.embedded_objects():
                self.add_object(sub_obj, resolve=resolve)

    def size(self):
        return sum([obj.size for obj in self.objects.values()])

    def link_repl(self, url, source_url):
        path = self.construct_link(url)
        if path is None:
            print 'Have not fetched anything with url', url
            return url
        source_path = self.construct_link(source_url)
        updirs = len(source_path.split('/'))-1
        if updirs:
            return '/'.join(['..']*updirs) + '/' + path
        else:
            return path

    def construct_link(self, url):
        if url not in self.objects:
            # Something we aren't serializing
            return None
        obj = self.objects[url]
        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        # we ignore scheme
        netloc = netloc.replace(':', '_')
        path = posixpath.normpath(path)
        path = netloc + path
        if query:
            path = path + '__' + query.replace('&', '_')
        ext = mimetypes.guess_extension(obj.type)
        if ext is None:
            print 'Cannot find extension for type %r' % obj.type
        if ext is not None and not path.endswith(ext):
            path += ext
        if fragment:
            path += '#' + fragment
        return path

    def serialize_to_dir(self, output_dir):
        for obj, path in self._serialize_objects():
            path = os.path.join(output_dir, path)
            dir = os.path.dirname(os.path.abspath(path))
            if not os.path.exists(dir):
                os.makedirs(dir)
            f = open(path, 'wb')
            f.write(obj.content)
            f.close()

    def serialize_to_zip(self, fp, compression=zipfile.ZIP_DEFLATED):
        z = zipfile.ZipFile(fp, 'w', compression=compression)
        for obj, path in self._serialize_objects():
            z.writestr(path, obj.content)
        z.close()

    def _serialize_objects(self):
        for url in sorted(self.objects):
            obj = self.objects[url]
            if obj.content is None:
                obj.read_content()
            obj = copy.copy(obj)
            obj.fixup_links(lambda url: self.link_repl(url, obj.url))
            path = self.construct_link(obj.url)
            yield obj, path

class Resource(object):

    def __init__(self, url, type=None, headers=None,
                 content=None):
        self.url = url
        self.type = type
        self.content = content
        self.headers = headers

    def __repr__(self):
        return '<%s %s %s type=%s>' % (
            self.__class__.__name__,
            hex(abs(id(self)))[2:],
            self.url, self.type or 'unknown')

    def rel_url(self, other_url):
        return urlparse.urljoin(self.url, other_url)

    def embedded_objects(self):
        return []

    def linked_objects(self):
        return []
    
    def read_content(self):
        if '#' in self.url:
            url, fragment = self.url.split('#', 1)
        else:
            url, fragment = self.url, None
        resp, self.content = http.request(self.url, 'GET')
        self.type = resp['content-type'].split(';')[0]
        for bad_header in ['Connection']:
            if bad_header in resp:
                del resp[bad_header]
        self.headers = resp.items()

    def size(self):
        if self.content is None:
            self.read_content()
        return len(self.content)

    def embedded_size(self):
        size = 0
        for obj in self.embedded_objects():
            size += obj.size()
        return size

    def total_size(self):
        return self.size() + self.embedded_size()

    def fixup_links(self, link_repl_func):
        pass

class Page(Resource):

    def __init__(self, url, content=None, doc=None,
                 headers=None):
        super(Page, self).__init__(
            url, headers=headers, content=content)
        if content and not doc:
            doc = etree.HTML(content)
        self.doc = doc
        self.type = 'text/html'

    def fixup_links(self, link_repl_func):
        assert self.doc is not None, (
            "fixup_links called before doc loaded in %r" % self)
        fixuplinks.fixup_links(self.doc, link_repl_func)
        self.content = htmlserialize.tostring(self.doc)

    def read_content(self):
        """
        Reads the content from the web
        """
        super(Page, self).read_content()
        # Should I decode the content charset?
        self.doc = etree.HTML(self.content)
        fragment = None
        if '#' in self.url:
            fragment = self.url.split('#', 1)[1]
        if fragment and False:
            ## FIXME: I don't think this is a good idea
            self.doc = extract_fragment(self.doc, fragment)
        def link_repl_func(href):
            return urlparse.urljoin(self.url, href)
        self.fixup_links(link_repl_func)

    def embedded_objects(self):
        assert self.doc is not None, (
            "embedded_objects called before doc loaded in %r" % self)
        objs = []
        for el in self.doc.xpath('//link'):
            if el.attrib.get('rel', '').lower() == 'stylesheet':
                objs.append(Stylesheet(self.rel_url(el.attrib['href']),
                                       type=el.attrib.get('type')))
            # Are there other types we care about?
        for el in self.doc.xpath('//script'):
            if el.attrib.get('src'):
                objs.append(Script(self.rel_url(el.attrib['src']),
                                   type=el.attrib.get('type')))
        for el in self.doc.xpath('//img'):
            objs.append(Image(self.rel_url(el.attrib['src']), el=el))
        for el in self.doc.xpath('//style'):
            if el.text:
                for ob_type, pat in [(Image, fixuplinks.CSS_URL_PAT),
                                     (Stylesheet, fixuplinks.CSS_IMPORT_PAT)]:
                    for match in pat.finditer(el.text):
                        objs.append(ob_type(self.rel_url(match.group(1))))
        # @@: Need to handle <object> and <embed>
        # Also iframes?
        for el in self.doc.xpath("//*[contains(@style, 'url(')]"):
            for match in fixuplinks.CSS_URL_PAT.finditer(el.attrib['style']):
                objs.append(Image(self.rel_url(match.group(1))))
        return objs

    def linked_objects(self):
        assert self.doc is not None, (
            "linked_objects called before doc loaded in %r" % self)
        objs = []
        for el in self.doc.xpath('//link'):
            if el.attrib['rel'].lower() != 'stylesheet':
                # Stylesheets are handled as embedded
                objs.append(Resource(self.rel_url(el.attrib['href']),
                                     type=el.attrib.get('type')))
        for el in self.doc.xpath('//a[@href]'):
            href = el.attrib['href']
            if (href.startswith('javascript:')
                or href.startswith('#')):
                continue
            href = href.split('#', 1)[0]
            objs.append(Page(self.rel_url(el.attrib['href'])))
        return objs

class Image(Resource):

    def __init__(self, url, type=None, el=None):
        super(Image, self).__init__(url, type=type)
        self.el = el

class Stylesheet(Resource):

    def embedded_objects(self):
        objs = []
        for match in fixuplinks.CSS_URL_PAT.finditer(self.content):
            # I'm going to guess this is an image
            objs.append(Image(self.rel_url(match.group(1))))
        for match in fixuplinks.CSS_IMPORT_PAT.finditer(self.content):
            # And that these are other stylesheets
            objs.append(Stylesheet(self.rel_url(match.group(1))))
        return objs

class Script(Resource):
    pass

            
def extract_fragment(doc, fragment):
    """
    Creates a new document that is like the given document, but
    contains only the identified fragment in the body.

    The fragment may be a normal fragment, or an xpath expression if
    it starts with '/' (url-decoded)

    If the fragment can't be found, then the entire document is
    returned as normal.
    """
    fragment = urllib.unquote(fragment)
    if fragment.startswith('/'):
        expr = fragment
    else:
        expr = "//*[@id='%s']" % fragment
    parts = doc.xpath(expr)
    if not parts:
        return doc
    new_doc = copy.deepcopy(doc)
    body = new_doc.xpath('//body')[0]
    for el in body:
        body.remove(el)
    body.extend(parts)
    return new_doc

