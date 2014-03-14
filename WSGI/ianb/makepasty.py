#!/usr/bin/env python
"""
This is a simple script to upload the current selection to the Pylons
pastebin.  When called, the selection is uploaded and the URL where it
is uploaded is put into the clipboard so you can paste it into IRC.

You might find this handy to bind to a key.

Note: this requires the following commands:
* xclip (Ubuntu package xclip)
"""

import urllib
import subprocess

paste_url = 'http://pylonshq.com/pasties/'

vars = {
    'notabot': 'most_likely',
    'author': 'Ian Bicking',
    'title': 'anonymous paste',
    'tags': '',
    }

def get_clip():
    p = subprocess.Popen(['xclip', '-o'], stdout=subprocess.PIPE)
    data = p.communicate()[0]
    return data

def set_clip(s):
    p = subprocess.Popen(['xclip', '-i'], stdin=subprocess.PIPE)
    p.communicate(s)

def detect_type(s):
    if s.strip().startswith('>>>'):
        return 'pycon'
    if s.strip().startswith('<'):
        return 'html'
    return 'python'

def submit_paste(data):
    f = urllib.urlopen(paste_url, urllib.urlencode(data))
    data = f.read()
    f.close()
    url = f.geturl()
    return url

def notify():
    subprocess.call(['beep', '-f', '2000', '-l', '100',
                     '-n', '-f', '500', '-l', '100'])

def main():
    s = get_clip()
    v = vars.copy()
    v['language'] = detect_type(s)
    v['code'] = s
    url = submit_paste(v)
    set_clip(url)
    # Not everyone wants this:
    notify()

if __name__ == '__main__':
    main()
    
