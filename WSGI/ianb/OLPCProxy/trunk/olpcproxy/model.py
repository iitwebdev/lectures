"""
Represents the storage
"""

import os
from urllib import quote as url_quote
from paste import fileapp
from pagecollector.model import ResourceCollection, Page

def base_quote(url):
    url = url.split('#', 1)[0]
    if isinstance(url, unicode):
        url = url.encode('utf8')
    return url_quote(url, '')

def safe_encode(obj, encoding='utf8'):
    if isinstance(obj, unicode):
        return obj.encode(encoding)
    return obj

class Storage(object):

    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.header_dir = os.path.join(data_dir, 'headers')
        self.dep_dir = os.path.join(data_dir, 'dependencies')
        for dir in self.data_dir, self.header_dir, self.dep_dir:
            if not os.path.exists(dir):
                os.mkdir(dir)

    def has_url(self, url):
        return (os.path.exists(self.url_filename(url))
                and os.path.exists(self.header_filename(url)))

    def url_cache_time(self, url):
        return os.path.getmtime(self.url_filename(url))

    def url_filename(self, url):
        return os.path.join(self.data_dir, base_quote(url))

    def header_filename(self, url):
        return os.path.join(self.header_dir, base_quote(url))

    def dep_filename(self, url, type):
        return os.path.join(self.dep_dir, type + '-' + base_quote(url))

    def static_serve_app(self, url):
        assert self.has_url(url)
        content_type, headers = self.read_headers(url)
        headers.append(('X-OLPCProxy-Internal', 'true'))
        filename = self.url_filename(url)
        return fileapp.FileApp(filename, headers=headers,
                               content_type=content_type)

    def read_headers(self, url):
        f = open(self.header_filename(url), 'rb')
        content_type = None
        headers = []
        for line in f:
            name, value = line.split(':', 1)
            value = value.strip()
            if name.lower() == 'content-type':
                content_type = value
            headers.append((name, value))
        return content_type, headers

    def save_page(self, url, headers, content, dep_url=None):
        url = safe_encode(url)
        dep_url = safe_encode(dep_url)
        content = safe_encode(content)
        f = open(self.url_filename(url), 'wb')
        f.write(content)
        f.close()
        f = open(self.header_filename(url), 'wb')
        for name, value in headers:
            f.write('%s: %s\n' % (name, value))
        f.close()
        if dep_url is not None:
            self.add_dependency(url, dep_url)

    def add_dependency(self, url, dep_url):
        f = open(self.dep_filename(dep_url, 'depends'), 'a')
        f.write(url + '\n')
        f.close()
        f = open(self.dep_filename(url, 'from'), 'a')
        f.write(dep_url)
        f.close()

    def remove_page(self, url):
        print 'removing page', url
        for fn in self.url_filename(url), self.header_filename(url):
            if os.path.exists(fn):
                os.unlink(fn)
        fn = self.dep_filename(url, 'from')
        if os.path.exists(fn):
            # These are a pages which rely on me; I'll still delete,
            # but I'll remove the dependency
            for dep_url in self._get_lines(fn):
                fn = self.dep_filename(dep_url, 'depends')
                self._remove_line(fn, url)
        fn = self.dep_filename(url, 'depends')
        if os.path.exists(fn):
            # These are pages that can potentially be collected as
            # garbage
            for dep_url in self._get_lines(fn):
                fn = self.dep_filename(dep_url, 'from')
                remaining = self._remove_line(fn, url)
                if not remaining:
                    self.remove_page(dep_url)
            if os.path.exists(fn):
                # Might have been deleted above
                os.unlink(fn)

    def _add_line(self, filename, line):
        if os.path.exists(filename):
            f = open(filename, 'ab')
            f.write('\n' + line)
            f.close()
        else:
            f = open(filename, 'wb')
            f.write(line)
            f.close()

    def _remove_line(self, filename, line):
        lines = self._get_lines(filename)
        if line not in lines:
            return
        lines.remove(line)
        if lines:
            f = open(filename, 'wb')
            f.write('\n'.join(lines))
            f.close()
        else:
            os.unlink(filename)
        return lines

    def _get_lines(self, filename):
        if not os.path.exists(filename):
            return []
        f = open(filename, 'rb')
        lines = f.read().splitlines()
        f.close()
        return lines

    def save_page_set(self, url,
                      headers=None, content=None):
        page_set = ResourceCollection()
        page = Page(url, content=content, headers=headers)
        if page.content is None:
            page.read_content()
        page_set.add_object(page)
        for obj in page_set.objects.values():
            if obj.url == url:
                dep_url = None
            else:
                dep_url = url
            if self.has_url(obj.url):
                continue
            if obj.content is None or obj.headers is None:
                obj.read_content()
            self.save_page(
                obj.url,
                obj.headers, obj.content,
                dep_url=dep_url)

