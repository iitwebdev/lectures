"""
Convenience factory for building and inserting mixed tag/text
structures.
"""

from lxml import etree

__all__ = ['tag', 'insert_beginning', 'append']

class TagSet(object):

    def __getattr__(self, tag):
        return Tag(tag)

tag = TagSet()

class Tag(object):

    def __init__(self, tag):
        self.tag = tag

    def __call__(self, *args, **kw):
        if 'c' in kw:
            args = args + (kw.pop('c'),)
        for name in kw.keys():
            if name.endswith('_'):
                kw[name[:-1]] = kw.pop(name)
        for name in kw.keys():
            if kw[name] is None:
                del kw[name]
            elif not isinstance(kw[name], basestring):
                kw[name] = unicode(kw[name])
        el = etree.Element(self.tag, kw)
        text, children = _flatten_children(flatten(args))
        el.extend(children)
        el.text = text
        return el

def _flatten_children(items):
    last = None
    text = None
    children = []
    for item in items:
        if isinstance(item, etree._Element):
            children.append(item)
            last = item
        else:
            if not isinstance(item, basestring):
                item = unicode(item)
            if last is None:
                if text is None:
                    text = item
                else:
                    text += item
            else:
                if last.tail:
                    last.tail += item
                else:
                    last.tail = item
    return text, children

def flatten(value):
    if not isinstance(value, (list, tuple)):
        return [value]
    result = []
    for item in value:
        result.extend(flatten(item))
    return result

def insert_beginning(el, *args):
    text, children = _flatten_children(flatten(args))
    if el.text:
        if children:
            if children[-1].tail:
                children[-1].tail += el.text
            else:
                children[-1].tail = el.text
        else:
            el.text = (text or '') + el.text
    else:
        if text:
            el.text = text
    el[:0] = children

def append(el, *args):
    text, children = _flatten_children(flatten(args))
    if text:
        if len(el):
            if el[-1].tail:
                el[-1].tail += text
            else:
                el[-1].tail = text
        else:
            el.text = text
    el.extend(children)

    
