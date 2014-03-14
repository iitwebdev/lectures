#!/usr/bin/env python
import sys
import subprocess
import re
import os

def bar(size):
    return '<img src="pixel.png" height="10" width="%i">' % size

def check_repo(svn_repo, html):
    p = subprocess.Popen(['svn', 'log', svn_repo],
                         stdout=subprocess.PIPE)
    output = p.communicate()[0]
    count = {}
    total = 0
    for line in output.splitlines():
        if re.search('^r[0-9]+', line):
            parts = line.split()
            username = parts[2]
            count[username] = count.get(username, 0)+1
            total += 1
    if html:
        print 'From repository: <a href="%s">%s</a>' % (
            svn_repo, svn_repo)
        print '<table class="svn-stats">'
        print ' <tr><th>Total commits:</th><th>%s</th><th></th>' % total
        print '     <th>%s</th></tr>' % bar(100)
    else:
        print 'Total commits:', total
    people = sorted(count.items(), key=lambda x: -x[1])
    for person, commits in people:
        percent = float(commits)*100/total
        if percent < 1:
            percent_s = '%0.1f%%' % percent
        else:
            percent_s = '%i%%' % percent
        if html:
            print ' <tr><td class="username">%s</td><td>%s</td><td>%s</td>' % (
                person, commits, percent_s)
            print '     <td>%s</td></tr>' % bar(percent)
        else:
            print '%15s  %4i  %5s' % (
                person, commits, percent_s)
    if html:
        print '</table>'


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        print 'Usage: %s svn_repository' % sys.argv[0]
        return
    svn_repo = args[0]
    check_repo(svn_repo, os.environ.get('HTML'))

if __name__ == '__main__':
    main()
