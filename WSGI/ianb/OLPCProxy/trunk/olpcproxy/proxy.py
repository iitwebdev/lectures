"""
Main proxy and rewriting code
"""

import time
import re
import urlparse
from wsgifilter import Filter
from wsgiproxy import exactproxy
from paste.request import construct_url
from paste.response import header_value, replace_header
from paste import httpexceptions
from lxml.etree import HTML
from wsgifilter.htmlserialize import tostring
from olpcproxy.factory import tag, insert_beginning, append
from hreviewparser import elquery

head_style = '''
div#olpc-top-message {
  background-color: #fff;
  color: #000;
  border: 2px solid #5f9410;
  font-family: sans-serif;
  font-size: small;
  font-weight: normal;
  position: absolute;
  z-index: 2000;
  -moz-border-radius: 3px;
  opacity: 1;
}

div#olpc-top-message.olpc-cached {
  background: url(%(static_url)s/arrow-down-round.gif) no-repeat #fff;
  padding: 0 0 0 18px;
}

div#olpc-top-message a {
  text-decoration: underline;
  color: #009;
}

a.olpc-cached {
  padding-left: 18px;
  background: url(%(static_url)s/arrow-down-round.gif) no-repeat;
}

img#olpc-close-image {
  vertical-align: top;
}

div.olpc-bundle {
  border: 4px solid #0d0;
  padding: 0.5em;
  margin: 0.5em;
}
'''

class OLPCFilter(Filter):

    decode_unicode = True

    save_key = '_olpc.savepage'
    remove_key = '_olpc.removepage'
    download_key = '_olpc.download'
    
    def __init__(self, app, store):
        self.store = store
        super(OLPCFilter, self).__init__(app)

    def __call__(self, environ, start_response):
        found = environ['olpcproxy.keys'] = []
        qs = environ.get('QUERY_STRING', '')
        parts = qs.split('&')
        for key in self.save_key, self.remove_key:
            if key in parts:
                parts.remove(key)
                found.append(key)
        downloads = environ['olpcproxy.downloads'] = []
        for part in list(parts):
            if part.startswith(self.download_key+'='):
                downloads.append(int(part[len(self.download_key)+1:]))
                parts.remove(part)
        qs = '&'.join(parts)
        environ['QUERY_STRING'] = qs
        return super(OLPCFilter, self).__call__(environ, start_response)

    def filter(self, environ, headers, data):
        url = construct_url(environ)
        static_url = environ['olpcproxy.static_url']
        found = environ['olpcproxy.keys']
        action = False
        if self.save_key in found:
            self.store.save_page_set(url, headers, data)
            action = True
        if self.remove_key in found:
            self.store.remove_page(url)
            action = True
        if environ.get('olpcproxy.downloads'):
            for index in environ['olpcproxy.downloads']:
                self.save_download(url, data, index)
            action = True
        if action:
            exc = httpexceptions.HTTPTemporaryRedirect(
                headers=[('Location', url)])
            raise exc
        if '?' not in url:
            url_query = url + '?'
        else:
            url_query = url + '&'
        has_page = self.store.has_url(url)
        page = HTML(data)
        try:
            head = page.xpath('//head')[0]
            body = page.xpath('//body')[0]
        except IndexError:
            # Not a full HTML page
            return data
        self.sub_links(url, page, static_url)
        if has_page:
            time_diff = time.time() - self.store.url_cache_time(url)
            time_diff = format_time_diff(time_diff)
            message = ['This page was cached %s ago.  You may '
                       % time_diff,
                       tag.a('remove it from the cache',
                              href=url_query+self.remove_key)]
            div_class = 'olpc-cached'
        else:
            message = ['This page is NOT cached.  You may ',
                       tag.a('add it to the cache',
                              href=url_query+self.save_key)]
            div_class = None
        if head_style:
            insert_beginning(
                head, tag.style(head_style % {'static_url': static_url},
                                 type="text/css"))
        image_location = static_url + '/x-small.gif'
        msg = tag.div(
            message,
            tag.a(tag.img(src=image_location, border=0, id="olpc-close-image"), href="#", onclick="document.getElementById('olpc-top-message').style.display='none'", valign="top"),
            id="olpc-top-message",
            class_=div_class)
        bundles = elquery.get_elements_by_class(body, 'olpc-bundle')
        if bundles:
            image_location = static_url + '/caution.gif'
            append(
                msg,
                tag.br(),
                tag.img(src=image_location),
                "Bundles were found in this page")
            for index, bundle in enumerate(bundles):
                b_msg = tag.div(
                    tag.a(tag.img(src=static_url+'/arrow-down-red.gif', border=0),
                          "You may download this bundle",
                          href=url_query+self.download_key+'='+str(index)))
                insert_beginning(bundle, b_msg)
        insert_beginning(body, msg, tag.br(clear="all"))
        data = tostring(page, True)
        # Now fix up the content-type:
        content_type = header_value(headers, 'content-type') or ''
        content_type = self._charset_re.sub('', content_type).strip().lstrip(';')
        content_type += '; charset=utf'
        replace_header(headers, 'content-type', content_type)
        return data

    def save_download(self, url, data, index):
        page = HTML(data)
        body = page.xpath('//body')[0]
        bundles = elquery.get_elements_by_class(body, 'olpc-bundle')
        bundle = bundles[index]
        links = bundle.xpath('descendant-or-self::a[@href]')
        for link in links:
            href = urlparse.urljoin(url, link.attrib['href'])
            print 'got one page:', href
            self.store.save_page_set(href)

    def sub_links(self, url, page, static_url):
        for link in page.xpath('//a[@href]'):
            href = urlparse.urljoin(url, link.attrib['href'])
            href = href.split('#', 1)[0]
            if href == url:
                continue
            if self.store.has_url(href):
                class_name = link.attrib.get('class', '')
                if class_name:
                    class_name += ' '
                class_name += 'olpc-cached'
                link.attrib['class'] = class_name
        

class OLPCStaticApp(object):

    def __init__(self, store):
        self.store = store

    def __call__(self, environ, start_response):
        exactproxy.filter_paste_httpserver_proxy_environ(environ)
        url = construct_url(environ)
        if self.store.has_url(url):
            app = self.store.static_serve_app(url)
            return app(environ, start_response)
        return exactproxy.proxy_exact_request(environ, start_response)
    
def make_olpc_proxy(store):
    app = OLPCStaticApp(store)
    app = OLPCFilter(app, store)
    app = httpexceptions.HTTPExceptionHandler(app)
    return app
        

MINUTE = 60
HOUR = 60*MINUTE
DAY = 24*HOUR
WEEK = 7*DAY
MONTH = 30*DAY
def format_time_diff(t):
    if t < MINUTE:
        return '%i sec' % t
    elif t < HOUR:
        return '%i min' % (t/MINUTE)
    elif t < DAY:
        return '%i hours' % (t/HOUR)
    elif t < WEEK:
        return '%i days' % (t/DAY)
    elif t < MONTH:
        return '%i weeks' % (t/WEEK)
    else:
        return '%i months' % (t/MONTH)
