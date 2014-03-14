import time
import sys
import os
import urllib
from cmdutils import OptionParser, CommandError, main_func
from lxml.html import HTML, tostring, Element
from lxml.html import defs
from lxml.etree import XPath, CommentBase
import copy
from itertools import count

## The long description of how this command works:
description = """\
"""

parser = OptionParser(
    usage="%prog [OPTIONS] FILES|URLS",
    version_package='PageSplitter',
    description=description,
    min_args=1,
    use_logging=True,
    )

parser.add_option(
    '-s', '--size',
    metavar="KILOBYTES",
    dest="size",
    help="The maximum size in kilobytes of the resulting documents.",
    default=100)

parser.add_verbose()

@main_func(parser)
def main(options, args):
    size = int(float(options.size) * 1000)
    logger = options.logger
    for file in args:
        split_file(file, size, logger)

def split_file(filename, size, logger):
    if (filename.lower().startswith('http:')
        or filename.lower().startswith('https:')):
        url = filename
        c = get_url_contents(url, logger)
        filename = url_to_filename(url)
        logger.notify('Saving %s as %s' % (url, filename))
        cur_size = len(c)
    else:
        cur_size = os.stat(filename).st_size
        if cur_size < size:
            logger.warn(
                "File %s already small enough (%sKb)"
                % (filename, cur_size/1000))
            return
        f = open(filename)
        c = f.read()
        f.close()

    logger.info(
        "Splitting %s into %sKb chunks (currently %sKb)" % (filename, size/1000, cur_size/1000))
    doc = HTML(c)
    body = doc.find('body') or doc
    big_el = find_big_block(body)
    parts = split_parts(doc, big_el, size, logger)
    prev = None
    pages = [(filename_for_index(filename, index), doc)
             for index, doc in enumerate(parts)]
    fixup_anchors(pages, logger)
    for (prev_fn, prev_doc), (fn, doc), (next_fn, next_doc) in paged(pages, (None, None)):
        head = doc.find('head')
        if prev_fn is not None:
            el = Element('link')
            el.set('rel', 'prev')
            el.set('href', prev_fn)
            head.append(el)
        if next_fn is not None:
            el = Element('link')
            el.set('rel', 'next')
            el.set('href', next_fn)
            head.append(el)
        c = tostring(doc, include_meta_content_type=True)
        logger.notify('Writing %sKb to %s'
                    % (len(c)/1000, fn))
        f = open(fn, 'w')
        f.write(c)
        f.close()

def fixup_anchors(pages, logger):
    ids = {}
    for fn, doc in pages:
        for el in doc.xpath('//*[@id]'):
            ids[el.get('id')] = fn
        for el in doc.xpath('//a[@name]'):
            ids[el.get('name')] = fn
    def link_repl(link):
        if link.startswith('#'):
            id = link[1:]
            if id in ids:
                if ids[id] == fn:
                    return link
                logger.debug('Rewriting anchor to %s#%s',
                             ids[id], id)
                return ids[id] + '#' + id
        return link
    for fn, doc in pages:
        doc.rewrite_links(link_repl, resolve_base_href=False)
        
def filename_for_index(base_fn, index):
    base, ext = os.path.splitext(base_fn)
    new_fn =  base + ('-%03i' % (index+1)) + ext
    return new_fn

def paged(seq, sentinal=None):
    prev = sentinal
    cur = sentinal
    empty = True
    for item in seq:
        if empty:
            # First run
            empty = False
        else:
            yield prev, cur, item
        prev = cur
        cur = item
    if not empty:
        yield prev, cur, sentinal

def split_parts(doc, big_el, size, logger):
    if len(tostring(big_el)) < size:
        return [doc]
    results = []
    while 1:
        if len(tostring(big_el)) < size:
            add_guessed_title(doc, big_el)
            results.append(doc)
            return results
        assert getroot(doc) is getroot(big_el)
        first_doc, first_big_el, new_doc, new_big_el = extract_chunk(doc, big_el, size, logger)
        add_guessed_title(first_doc, first_big_el)
        results.append(first_doc)
        doc = new_doc
        big_el = new_big_el

split_tags = defs.general_block_tags + [
    'dl', 'table', # FIXME: lists ol/ul?
    ]

def extract_chunk(doc, big_el, size, logger):
    assert len(doc), 'document must have children'
    for el, el_size in yield_sizes(big_el):
        if el.tag not in split_tags:
            continue
        if el_size > size:
            break
    (pre_split, pre_big), (post_split, post_big) = split_on_element(el, big_el)
    pre_doc = getroot(pre_split)
    post_doc = getroot(post_split)
    return (pre_doc, pre_big, post_doc, post_big)

def add_guessed_title(doc, container):
    """
    See if the document has an <h1> or <h2> tag that can be used as the subdocument
    title prefix.  If found, add that prefix to the <title>
    """
    for el in container.xpath('descendant-or-self::h1 | descendant-or-self::h2'):
        title = el.text_content().strip()
        if len(title) > 40:
            title = title[:35] + '...'
        cur_title = doc.xpath('//head/title')
        if cur_title:
            cur_title = cur_title[0]
        else:
            cur_title = Element('title')
            doc.find('head').append(cur_title)
        cur_title.text = title + ' | ' + (cur_title.text or '')
        return

def find_big_block(doc, portion=0.90):
    """
    Find the subelement of doc that contains at least portion (default
    0.90=90%) of the total document, measured textually.
    """
    total = len(tostring(doc))
    last = doc
    next = doc
    while 1:
        for item in next:
            if len(tostring(item)) >= total * portion:
                last = next = item
                break
        else:
            break
    return last

def split_on_element(split_el, stop_el=None):
    """
    Split a document at split_el, analagous to [:split_el] and
    [split_el:] (the split_el goes in the second item returned).

    stop_el is an element above which the document won't be split; it
    will only be copied.  So, for instance, if you give the body tag
    as stop_el, both return results will have identical head tags
    (otherwise the first return value would have the head, and the
    second would have no head; in both cases they will still have a
    body).

    Examples::

        >>> from lxml.html import usedoctest
        >>> h = HTML('''<html><body>
        ... <div id="container">
        ... <div id="foo"></div>
        ... <div><b>middle</b> text</div>
        ... <div class="section">
        ... blah blah blah
        ... <div id="bar"></div>
        ... blah blugh blah
        ... </div>
        ... tail text</div>
        ... </body></html>''')
        >>> foo = h.get_element_by_id('foo')
        >>> bar = h.get_element_by_id('bar')
        >>> container = h.get_element_by_id('container')
        >>> pre_result, post_result = split_on_element(bar, container)
        >>> print tostring(getroot(pre_result[0]))
        <html>
         <body>
          <div id="container">
            <div id="foo"></div>
            <div><b>middle</b> text</div>
            <div class="section">
             blah blah blah
            </div>
          </div>
         </body>
        </html>
        >>> print tostring(getroot(post_result[0]))
        <html>
         <body>
          <div id="container">
           <div class="section">
            <div id="bar"></div>
            blah blugh blah
           </div>
           tail text
          </div>
         </body>
        </html>
    
    """
    pre_split_el, pre_stop_el = copy_elements(split_el, stop_el)
    post_split_el, post_stop_el = copy_elements(split_el, stop_el)
    pre_doc = getroot(pre_split_el)
    post_doc = getroot(post_split_el)
    pre_el = pre_split_el
    while 1:
        if pre_el is pre_stop_el:
            break
        parent = pre_el.getparent()
        if parent is None:
            if pre_stop_el is None:
                break
            else:
                assert 0, "Did not encounter stop_el %s" % pre_stop_el
        index = parent.index(pre_el)
        if pre_el is pre_split_el:
            del parent[index:]
        else:
            del parent[index+1:]
        parent.tail = None
        pre_el = parent
    post_el = post_split_el
    while 1:
        if post_el is post_stop_el:
            break
        parent = post_el.getparent()
        if parent is None:
            if post_stop_el is None:
                break
            else:
                assert 0, "Did not encounter stop_el %s" % post_stop_el
        index = parent.index(post_el)
        del parent[:index]
        parent.text = None
        post_el = parent
    return (pre_split_el, pre_stop_el), (post_split_el, post_stop_el)

def copy_elements(*elements):
    """
    Copy a sequence of elements, returning the copied sequence.  The
    copied elements will all come from a single copy of the common
    root document that all the elements share.

    Example::

        >>> h = HTML('''<html><body>
        ... <div id="foo"></div>
        ... <div id="bar"></div>
        ... </body></html>''')
        >>> foo = h.get_element_by_id('foo')
        >>> bar = h.get_element_by_id('bar')
        >>> new_foo, new_bar = copy_elements(foo, bar)
        >>> foo is new_foo
        False
        >>> bar is new_bar
        False
        >>> new_foo.get('id')
        'foo'
        >>> new_bar.get('id')
        'bar'
        
    """
    if not elements:
        raise TypeError("You must give at least one element")
    ids = []
    doc = getroot(elements[0])
    counter = count()
    for el in elements:
        assert getroot(el) is doc
        if el is None:
            ids.append(None)
        else:
            id = '%s-%s' % (str(time.time()), counter.next())
            ids.append(id)
            el.set('copy__id', id)
    new_doc = copy.deepcopy(doc)
    result = []
    for id in ids:
        if id is None:
            result.append(None)
        else:
            el = _copy_id_xpath(new_doc, id=id)[0]
            del el.attrib['copy__id']
            result.append(el)
    for new, old in zip(elements, result):
        if new is None:
            assert old is None
        else:
            assert new.tag == old.tag
    return result

_copy_id_xpath = XPath('//*[@copy__id=$id]')

def getroot(el):
    """
    Get the root element from the given element's tree.
    """
    return el.getroottree().getroot()

def _one_tag_length(el):
    if isinstance(el, CommentBase):
        return 6+len(el.text)
    return (2 + len(el.tag or '')
            + sum([len(key)+len(value)+3
                   for key, value in el.attrib.items()] or [0]))

def _element_length(el):
    if el is None:
        return 0
    elif isinstance(el, CommentBase) or el.tag == 'meta':
        return _one_tag_length(el)
    else:
        return len(tostring(el))

def yield_sizes(el):
    """
    Yield (element, accumulated_size), iterating through the entire
    document.

    Returns elements in depth-first order, with increasing accumulated
    size.  The accumulated size can sometimes be slightly inaccurate.

    Example::

        >>> h = HTML('''<html><body>
        ... <h1>test</h1>
        ... <div>Some text <b>another test</b> and more</div>
        ... <p>and more text</p>
        ... </body></html>''')
        >>> for el, size in yield_sizes(h):
        ...     print el.tag, size
        h1 27
        b 62
        div 77
        p 98
        body 106
        html 113

    """
    size = _one_tag_length(el) + len(el.text or '')
    for child in el:
        subchild = None
        for subchild, subsize in yield_sizes(child):
            yield (subchild, subsize+size)
        if subchild is not None and subchild.tag == 'meta' or isinstance(el, CommentBase):
            size += subsize
        else:
            size += _element_length(child)
    yield el, _element_length(el)

def get_url_contents(url, logger):
    logger.notify('Fetching %s' % url)
    f = urllib.urlopen(url)
    c = f.read()
    f.close()
    h = HTML(c)
    h.make_links_absolute(url)
    return tostring(h)

def url_to_filename(url):
    fn = url.split('/')[-1]
    fn = fn.replace('\\', '')
    fn = fn.split('?', 1)[0]
    base = os.path.splitext(fn)[0]
    if not base:
        base = 'index'
    fn = base + '.html'
    return fn

if __name__ == '__main__':
    if os.environ.get('DOCTEST'):
        import doctest
        doctest.testmod()
    else:
        main()
