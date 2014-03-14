import urlparse
import re
import os
import urllib
# posixpath works with URL-style filenames; os.path doesn't on Windows:
import posixpath

def map_url(url, mime_type, pref_ext, options):
    """
    Gets a URL as input, and returns the filename where it should go.  The filename
    should not be absolute.
    """
    scheme, netloc, path, qs, fragment = urlparse.urlsplit(url)
    # we don't care about the scheme
    # or the port:
    netloc = netloc.split(':')[0]
    ## Kind of a Plone-specific hack:
    #if path.endswith('/view'):
    #    path = path[:-5]
    if (options.get('base_path')
        and path.startswith(options['base_path'])):
        path = path[len(options['base_path']):]
    if (options.get('base_path')
        and path + '/' == options['base_path']):
        path = ''
    path = os.path.splitext(path)[0]
    path = urllib.unquote(path)
    path = clean(path)
    if not path:
        path = 'index'
    if qs:
        path += '_' + qs
    path += pref_ext
    return path
    
spacish_chars = re.compile(
    r'[ \t\n]+')
unsafe_chars = re.compile(
    r'[^a-zA-Z0-9_.()!/-]')
def clean(path):
    path = spacish_chars.sub(' ', path)
    path = unsafe_chars.sub('', path)
    path = path.strip('/.')
    return path

def rewrite_line(orig_url, new_path, options):
    return '%s %s\n' % (orig_url, new_path)
