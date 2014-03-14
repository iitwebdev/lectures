import time
from cgi import escape as cgi_escape
from htmlescape import escape as html_escape

def pt_escape(s, quote=0):
    """Replace special characters '&', '<' and '>' by SGML entities.

    If string is set to False, we are dealing with Unicode input.
    """
    if '&' in s:
        s = s.replace("&", "&amp;") # Must be done first!
    if '<' in s:
        s = s.replace("<", "&lt;")
    if '>' in s:
        s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

comparisons = [
    ("cgi.escape", cgi_escape),
    ("htmlescape.escape", html_escape),
    ("z3c.pt escape", pt_escape),
    ]

strings = []
for i in range(100000):
    strings.append("<>\"&abcdefghijklmnopqrstuvwxyz"*20)
    if i % 2:
        strings[-1] = strings[-1].replace('x', '&');

def test_time(name, func, ref=None, reps=10000):
    start = time.time()
    for s in strings:
        result = func(s, True)
    total = time.time() - start
    if ref is None:
        ref = total
    percentage = 100*total/ref
    print "%30s: %4.2fsec  (%3i%%)" % (name, total, percentage)
    return total

def test_all():
    ref = None
    for name, func in comparisons:
        result = test_time(name, func, ref=ref)
        if ref is None:
            ref = result

if __name__ == '__main__':
    test_all()
