"""
Routines to get elements from lxml trees
"""
import re
import cgi
from lxml.etree import tostring
from hreviewparser.parselog import dummy

class ElementNotFound(IndexError):
    """
    Raised when an element is expected, but not found
    """

def get_parent_with_class(el, class_name, log=dummy):
    """
    Gets the first parent of `el` that has the given class (or raise
    `ElementNotFound`)
    """
    parent = el
    regex = re.compile(r'\b%s\b' % class_name)
    while parent:
        class_name = parent.attrib.get('class')
        if class_name and regex.search(class_name):
            return parent
        parent = parent.getparent()
    raise ElementNotFound("No parent of %r with class_name=%r"
                          % (el, class_name))

def get_rel_link(el, rel, log=dummy):
    """
    Get the href and element of a single element inside `el`
    that is like ``<a rel={rel}>``, or raise `ElementNotFound`
    """
    els = get_rel_links(el, rel, log=log)
    if not els:
        raise ElementNotFound()
    if len(els) > 1:
        log.warn(
            'Multiple <a rel="%s"> found: %s'
            % (rel, ', '.join(map(tostring, els))))
    link_el = els[0]
    link = link_el.attrib['href']
    return link, link_el

def get_rel_links(el, rel, log=dummy):
    """
    Return all links with the given ``rel={rel}``.
    """
    return el.xpath("descendant-or-self::a[@rel='%s']" % rel)

def get_single_item(el, name, log=dummy):
    """
    Get a single value and element with the given class name.
    """
    el = get_single_el(el, name, log=log)
    if el.attrib.get('title'):
        value = html_quote(el.attrib['title'])
    else:
        value = get_contents(el)
    return value, el

def html_quote(s):
    if s is None:
        return ''
    else:
        return cgi.escape(unicode(s), 1)

def get_contents(el):
    """
    Return the contents of the element; either the text, or mixed
    text+markup for the item.
    """
    parts = [el.text or '']
    for part in el.getchildren():
        parts.append(tostring(part))
    return norm_whitespace(''.join(parts))

def strip_tags(text):
    """
    Strip any tags from a piece of text
    """
    text = re.sub(r'<.*?>', '', text)
    text = norm_whitespace(text.strip())
    return text

_whitespace_re = re.compile(r'[\s][\s]+')
def norm_whitespace(text):
    return _whitespace_re.sub(' ', text)

def get_single_el(el, class_name, log=dummy):
    """
    Get a single element with the given class name.
    """
    els = get_elements_by_class(el, class_name)
    if not els:
        raise ElementNotFound(
            "No element with class %r" % class_name)
    if len(els) > 1:
        log.warn(
            "Multiple elements found with class %r: %s",
            class_name, ', '.join([tostring(el).strip().replace('\n', '')
                                   for el in els]))
    return els[0]

def contains_class_xpath(class_names, prefix="descendant-or-self::*"):
    """
    Returns the xpath expression for elements that contain the class
    name.
    """
    if isinstance(class_names, basestring):
        class_names = [class_names]
    expr = ' or '.join(
        ["contains(concat(' ', translate(@class, '\n\r\t', '   '), ' '), ' %s ')" % class_name
         for class_name in class_names])
    return "%s[%s]" % (prefix, expr)

def get_elements_by_class(node, class_names):
    """
    Returns all elements with any of the given class names.  A single
    class_name may also be passed in.
    """
    return node.xpath(contains_class_xpath(class_names))
