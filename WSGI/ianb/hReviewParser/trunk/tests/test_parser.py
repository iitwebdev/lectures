import os
from lxml import etree
from hreviewparser import parse_hreviews
from hreviewparser import parselog

example_dir = os.path.join(os.path.dirname(__file__), 'examples')

def load_doc():
    fn = os.path.join(example_dir, 'examples.html')
    f = open(fn, 'rb')
    content = f.read()
    f.close()
    doc = etree.HTML(content)
    return doc

def get_element(doc, id):
    result = list(doc.xpath("//*[@id='%s']" % id))
    if not result:
        raise LookupError(
            "Nothing matches id %r" % id)
    if len(result) > 1:
        raise LookupError(
            "Too many matches for id %r: %s"
            % (id, result))
    return result[0]

def parse_element(id):
    doc = load_doc()
    el = get_element(doc, id)
    print '--document:'+('-'*30)
    print etree.tostring(el.xpath("descendant::*[@class='hreview']")[0])
    log = parselog.ParseLog()
    results = parse_hreviews(el, log=log)
    assert len(results) == 1
    print '--log:'+('-'*30)
    print log
    return results[0]

def test_simple():
    review = parse_element('simplest')
    assert review.item.url == 'http://localhost/1'
    assert review.item.fn == 'simplest 1'
    
def test_decription():
    review = parse_element('simple-with-description')
    assert review.item.url == 'http://localhost/2'
    assert review.item.fn == 'simplest 2'
    desc = etree.tostring(review.description)
    assert 'okay link' in desc
    assert 'better stuff' in desc

def test_with_tag():
    review = parse_element('with-tag')
    assert review.description is not None
    tags = review.tags
    assert len(tags) == 2
    assert tags[0].uri == 'http://localhost/tags/alpha'
    assert tags[1].uri == 'http://localhost/tags/beta'
    
def test_boogdesign():
    review = parse_element('boogdesign')
    assert review.description is not None
    tags = review.tags
    print tags
    print review
    assert 0
