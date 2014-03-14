#!/usr/bin/env python

import re

subbers = [
    (r'<head>', '''<head>
    <meta name="version" content="S5 1.0" />
    <link rel="stylesheet" href="ui/slides.css" type="text/css" media="projection" id="slideProj" />
    <link rel="stylesheet" href="ui/opera.css" type="text/css" media="projection" id="operaFix" />
    <link rel="stylesheet" href="ui/print.css" type="text/css" media="print" id="slidePrint" />
    <script src="ui/slides.js" type="text/javascript"></script>'''),
    (r'<body>', '''<body>
    <div class="layout">
    <div id="currentSlide"></div>
    <div id="header"></div>
    <div id="footer">
    '''),
    (r'</body>', '''</div></body>'''),
    (r'<div class="section"[^>]*>\s*<h1>', '<div class="slide"><h1>'),
    (r'<div class="document"[^>]*>', ''),
    (r'<h1 class="title">(.*)</h1>', r'''
    <h1>\1</h1>
    <div id="controls"></div>
    </div>
    <div class="presentation">
    '''),
    ]

def convert(content):
    for regex, repl in subbers:
        content = re.sub(regex, repl, content)
    return content

if __name__ == '__main__':
    import sys
    if sys.argv[1:]:
        input = open(sys.argv[1]).read()
    else:
        input = sys.stdin.read()
    result = convert(input)
    if sys.argv[2:]:
        open(sys.argv[2], 'w').write(result)
    else:
        sys.stdout.write(result)
