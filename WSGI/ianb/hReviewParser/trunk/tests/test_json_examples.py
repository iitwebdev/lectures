import os
from lxml import etree
from hreviewparser import parse_hreviews
from hreviewparser import parselog
from simplejson import load as json_load
from pprint import pprint
from dictcompare import compare

spec_dir = os.path.join(os.path.dirname(__file__), 'examples',
                        'from-microformat.org')

def example_filenames():
    for fn in os.listdir(spec_dir):
        fn = os.path.join(spec_dir, fn)
        if not fn.endswith('.html'):
            continue
        yield fn, os.path.splitext(fn)[0]+'.json'

def load_example(filename):
    f = open(filename, 'rb')
    content = f.read()
    f.close()
    doc = etree.HTML(content)
    log = parselog.ParseLog()
    results = parse_hreviews(doc, log=log)
    assert len(results) == 1
    if log.messages:
        print '--log:'+('-'*30)
        print log
    print '--doc:'+('-'*30)
    print etree.tostring(results[0].el)
    print '-'*36
    return results[0]

def load_json(filename):
    f = open(filename, 'rb')
    data = json_load(f)
    f.close()
    return data

def test_all_examples():
    for html, json in example_filenames():
        yield example_tester, html, json

def example_tester(html_filename, json_filename):
    example = load_example(html_filename)
    example_json = example.jsonable()
    json = load_json(json_filename)
    assert len(json) == 1
    json = json[0]
    # @@: We don't handle reviewer yet:
    delkeys([example_json, json], 'reviewer', 'rated_tags', 'unrated_tags')
    if 'all_tags' in json:
        json['tags'] = json.pop('all_tags')
    if 'vcard' in json['item']:
        # @@: Don't handle this either
        delkeys([example_json, json], 'item')
    assert compare(example_json, json)

def delkeys(ds, *keys):
    if not isinstance(ds, (list, tuple)):
        ds = [ds]
    for key in keys:
        for d in ds:
            if key in d:
                del d[key]
