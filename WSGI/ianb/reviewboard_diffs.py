#!/usr/bin/env python
"""
Script sends all files as a diff to a reviewboard instance
"""

import optparse
import sys
import difflib
import os
try:
    import restclient
except ImportError:
    print 'You must install restclient'
    print '  easy_install restclient'
    raise

parser = optparse.OptionParser(
    usage='%prog [OPTIONS] REVIEW_URL [FILES...]')
parser.add_option(
    '-a', '--auth',
    dest='auth',
    help='The auth/session cookie (put in "javascript:document.write(document.cookie)" to view it)')
parser.add_option(
    '-d', '--directory',
    dest='directories',
    action='append',
    default=['.'],
    help='Directory to search for files in.  Default cwd; can use multiple times')
parser.add_option(
    '-e', '--ext',
    dest='extensions',
    action='append',
    default=['.py', '.mako'],
    help="Extensions to search for.  Default .py and .make; can use multiple times")
parser.add_option(
    '-b', '--base',
    default='/',
    dest='repo_base',
    help="Repository base (e.g., --base=/proj/trunk)")
parser.add_option(
    '-r', '--repo',
    dest='repo',
    help="Repository id (an integer)")
parser.add_option(
    '--append',
    dest='append',
    help="Review to append diffs to (an integer)")

class BadCommand(Exception):
    pass

def find_files(dir, exts):
    for dirpath, dirnames, filenames in os.walk(dir):
        for fn in filenames:
            for ext in exts:
                if fn.endswith(ext):
                    yield os.path.join(dirpath, fn)
                    break

def upload_file(options, fn):
    diff = make_diff(fn)
    if diff is None:
        return
    if not options.append:
        url = options.app_url + 'r/new/'
        field_name = 'diff_path'
    else:
        url = options.app_url + 'api/json/reviewrequests/%s/diff/new/' % options.append
        field_name = 'path'
    params = {'basedir': options.repo_base}
    if options.repo:
        params['repository'] = options.repo
    headers, body = restclient.POST(
        url,
        params=params,
        files={field_name: {'file': diff, 'filename': fn+'.diff', 'content-type': 'text/x-patch'}},
        headers={'Cookie': options.auth},
        async=False,
        resp=True)
    if options.repo:
        if not headers['status'].startswith('302'):
            print 'Error:'
            print body
            print '-'*60
            print 'Aborting'
            sys.exit(3)
        print '-> Created %s' % headers['location']
    else:
        if not body.startswith('{"stat": "ok"'):
            print 'Error:'
            print body
            print '-'*60
            print 'Aborting'
            sys.exit(3)
        print '-> Appended to %s' % options.append
        print body

def make_diff(fn):
    content = open(fn).read().splitlines()
    if not content:
        return None
    lines = list(difflib.unified_diff([], content, fn, fn))
    lines[0] = lines[0].rstrip() + '    (revision 0)'
    lines[1] = lines[1].rstrip() + '    (revision 0)'
    lines[2] = lines[2].rstrip()
    return '\n'.join(lines)

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)
    if not args:
        raise BadCommand('You must provide a review URL (e.g., http://localhost:8080/)')
    options.app_url = args[0]
    if not options.app_url.endswith('/'):
        options.app_url += '/'
    if not options.auth:
        raise BadCommand('You must provide --auth=something')
    if not options.auth.startswith('sessionid='):
        options.auth = 'sessionid=%s' % options.auth
    if not options.repo and not options.append:
        raise BadCommand('You must provide a --repo=ID or --append=ID')
    if options.repo and options.append:
        raise BadCommand('You may only provide one of --repo or --append')
    if options.repo:
        try:
            options.repo = int(options.repo)
        except ValueError:
            raise BadCommand('Bad value for --repo (%r)' % options.repo)
    elif options.append:
        try:
            options.append = int(options.append)
        except ValueError:
            raise BadCommand('Bad value for --append (%r)' % options.append)
    if len(args) > 1:
        files = args[1:]
    else:
        files = []
        for dir in options.directories:
            files.extend(find_files(dir, options.extensions))
    for file in files:
        print 'Uploading %s' % file
        upload_file(options, file)

if __name__ == '__main__':
    try:
        main()
    except BadCommand, e:
        print e
        sys.exit(1)

    
