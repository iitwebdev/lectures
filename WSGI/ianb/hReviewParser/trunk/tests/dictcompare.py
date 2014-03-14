from formencode.doctest_xml_compare import xml_compare
from lxml import etree

def compare(got, expected):
    if got == expected:
        return True
    if not (isinstance(got, dict) and isinstance(expected, dict)):
        return False
    same = []
    different = []
    missing_got = expected.keys()
    missing_expected = []
    for key in got:
        if key in missing_got:
            missing_got.remove(key)
        if key not in expected:
            missing_expected.append(key)
        elif not compare_items(got[key], expected[key], key):
            different.append(key)
        else:
            same.append(key)
    if not missing_got and not missing_expected and not different:
        return True
    if same:
        print 'Matching keys: %s' % join_keys(same)
    else:
        print 'No matching keys'
    if missing_got:
        print "Keys expected that weren't got:"
        for key in missing_got:
            print "  %s=%r" % (key, expected[key])
    if missing_expected:
        print "Keys got that weren't expected:"
        for key in missing_expected:
            print "  %s=%r" % (key, got[key])
    for key in sorted(different):
        got_key = got[key]
        expected_key = expected[key]
        if isinstance(got_key, unicode) or isinstance(expected_key, unicode):
            got_key = unicode(got_key)
            expected_key = unicode(expected_key)
        print "Key %s:" % key
        print "  got=     %r" % got_key
        print "  expected=%r" % expected_key
    return False

def compare_items(got, expected, hint=None):
    if (isinstance(got, basestring)
        and isinstance(expected, basestring)
        and got.startswith('<')
        and expected.startswith('<')):
        def reporter(value):
            if hint:
                print '%s: %s' % (hint, value)
            else:
                print value
        try:
            got = etree.XML('<xml>%s</xml>' % got)
        except Exception, e:
            reporter('Error parsing %r: %s' % (got, e))
            return False
        try:
            expected = etree.XML('<xml>%s</xml>' % expected)
        except Exception, e:
            reporter('Error parsing %r: %s' % (expected, e))
            return False
        return xml_compare(got, expected, reporter=reporter)
    return got == expected

def join_keys(keys):
    return ', '.join(map(repr, sorted(keys)))
