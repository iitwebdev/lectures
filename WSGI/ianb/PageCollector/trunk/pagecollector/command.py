import sys
import os
import optparse
import urlparse
import pkg_resources
import mimetypes
from pagecollector.model import ResourceCollection, Page
import fnmatch
import re
import posixpath

dist = pkg_resources.get_distribution('PageCollector')

help = """\
Get all the pages from SITE"""

parser = optparse.OptionParser(
    version='%s from %s (python %s)'
    % (dist, dist.location, sys.version),
    usage='%prog [OPTIONS] SITE [more URLs...]\n\n'+help)

parser.add_option(
    '-o', '--output',
    dest="output",
    metavar="DIR",
    help="Where to write the output (by default goes in a directory named after the site host)")

parser.add_option(
    '-r', '--recurse',
    dest="recurse",
    metavar="LEVEL",
    default="1",
    type="int",
    help="Level to recurse to (default 1)")

parser.add_option(
    '-H', '--host',
    dest="hosts",
    metavar="HOST",
    action="append",
    help="Host to cross to (by default stay on one host); wildcards allowed")

parser.add_option(
    '--base',
    dest="base_url",
    metavar="URL",
    help="Base URL (no links below this will be fetched)")

parser.add_option(
    '-m', '--mapper',
    dest="mapper",
    metavar="PYTHON_FILE",
    default="pagecollector.default_mapper",
    help="Python file that defines functions to map URLs to files, and how to write the redirects")

parser.add_option(
    '-M', '--option',
    dest="mapper_options",
    action="append",
    metavar="NAME:VALUE",
    help="Option(s) that will be passed to the mapper functions")

parser.add_option(
    '--redir',
    dest="redir",
    metavar="FILENAME",
    default="redirects.txt",
    help="Where to write out redirects")

parser.add_option(
    '-v', '--verbose',
    dest="verbose",
    action="count",
    help="Be more verbose (use multiple times to increase)")

parser.add_option(
    '-q', '--quiet',
    dest="quiet",
    action="count",
    help="Be less verbose")

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    options, args = parser.parse_args(args)
    if len(args) < 1:
        print "Please enter one SITE"
        parser.print_help()
        sys.exit(1)
    urls = args
    mapper_options = {}
    for value in options.mapper_options or []:
        if ':' not in value:
            print 'Bad argument to --option: %r' % value
            parser.print_help()
            sys.exit(1)
        name, value = value.split(':', 1)
        mapper_options[name] = value
    mapper = options.mapper
    if mapper.endswith('.py'):
        mapper_mod = new.module('__mapper__')
        execfile(mapper, mapper_mod.__dict__)
    else:
        from paste.util import import_string
        mapper_mod = import_string.simple_import(mapper)
    output = options.output
    if not output:
        output = urlparse.urlsplit(urls[0])[1]
    verbosity = 1 + (options.verbose or 0) - (options.quiet or 0)
    if not options.hosts:
        options.hosts = [urlparse.urlsplit(urls[0])[1].split(':')[0]]
    url_matcher = URLMatcher(options.hosts, options.base_url, verbosity)
    mapper_options['url_matcher'] = url_matcher
    mapper_options['host_options'] = options.hosts
    mapper_options['base_url'] = options.base_url
    if options.base_url:
        mapper_options['base_path'] = urlparse.urlsplit(options.base_url)[2]
    mapper_options['urls'] = urls
    policy = Policy(mapper_mod, mapper_options)
    run_command(urls, output, policy, options.redir, verbosity, options.recurse,
                url_matcher)

class URLMatcher(object):

    def __init__(self, hosts, base_url, verbosity):
        self.regexes = []
        if not hosts:
            return
        for host in hosts:
            self.regexes.append(re.compile('^' + fnmatch.translate(host), re.I))
        self.base_url = None
        if base_url and not self(base_url):
            raise ValueError(
                "The base URL %s doesn't match the allowed hosts: %s"
                % (base_url, ', '.join(hosts)))
        if base_url:
            self.base_url = base_url.rstrip('/') + '/'
        self.verbosity = verbosity
        
    def __call__(self, url):
        if self.base_url:
            if (not url.startswith(self.base_url)
                and url+'/' != self.base_url):
                if self.verbosity > 1:
                    print "Skipping URL %s (doesn't start with %s)" % (url, self.base_url)
                return False
        host = urlparse.urlsplit(url)[1].split(':', 1)[0]
        if not self.regexes:
            return True
        for regex in self.regexes:
            if regex.search(host):
                return True
        if self.verbosity > 1:
            print "Skipping URL %s (wrong host)" % url
        return False

class Policy(object):

    def __init__(self, mapper_mod, mapper_options):
        self.mapper_mod = mapper_mod
        self.mapper_options = mapper_options
        self.cached_filenames = {}
        self.used_filenames = set()
        self.used_directories = set()

    def map_url(self, url, mime_type, pref_ext=None):
        if url in self.cached_filenames:
            return self.cached_filenames[url]
        if pref_ext is None:
            pref_ext = mimetypes.guess_extension(mime_type)
            if pref_ext is None:
                scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
                pref_ext = posixpath.splitext(path)[1]
        filename = self.mapper_mod.map_url(url, mime_type, pref_ext, self.mapper_options)
        filename = self.unique_filename(filename)
        self.cached_filenames[url] = filename
        return filename

    def rewrite_line(self, url, filename):
        return self.mapper_mod.rewrite_line(url, filename, self.mapper_options).strip()

    def unique_filename(self, filename):
        parts = self.split_filename(filename)
        filename = None
        while parts:
            if filename:
                filename += '/' + parts.pop(0)
            else:
                filename = parts.pop(0)
            is_full = not bool(parts)
            filename = self.unique_segment(filename, is_full)
        return filename

    def unique_segment(self, filename, is_full):
        if (filename not in self.used_filenames
            and filename not in self.used_directories):
            if is_full:
                self.used_filenames.add(filename)
            else:
                self.used_directories.add(filename)
            return filename
        if filename not in self.used_filenames and not is_full:
            return filename
        base, ext = os.path.splitext(filename)
        count = 2
        while 1:
            filename = '%s-%s%s' % (base, count, ext)
            if (filename not in self.used_filenames
                and filename not in self.used_directories):
                if is_full:
                    self.used_filenames.add(filename)
                else:
                    self.used_directories.add(filename)
                break
            if filename not in self.used_filenames and not is_full:
                break
            count += 1
        return filename

    def split_filename(self, filename):
        parts = []
        filename = os.path.normpath(filename)
        while filename:
            parts.insert(0, os.path.basename(filename))
            filename = os.path.dirname(filename)
        return parts

class SavingCollection(ResourceCollection):

    def __init__(self, policy):
        self.policy = policy
        super(SavingCollection, self).__init__()

    def construct_link(self, url):
        if url not in self.objects:
            # Something we aren't serlializing
            return None
        obj = self.objects[url]
        filename = self.policy.map_url(url, obj.type)
        return filename

def run_command(urls, output, policy, redir_filename, verbosity, recurse,
                url_matcher):
    col = SavingCollection(policy)
    for url in urls:
        page = Page(url)
        collect_objects(col, page, recurse, verbosity, url_matcher)
    col.serialize_to_dir(output)
    if redir_filename:
        redir_dir = os.path.dirname(os.path.abspath(redir_filename))
        redirs = []
        if not os.path.exists(redir_dir):
            if verbosity >= 1:
                print 'Making directory', redir_dir
            os.makedirs(redir_dir)
        for url, filename in policy.cached_filenames.items():
            redirs.append(policy.rewrite_line(url, filename))
        if verbosity >= 2:
            print 'Writing %s redirects to %s' % (len(redirs), redir_filename)
        f = open(redir_filename, 'w')
        f.write('\n'.join(redirs))
        f.close()

def collect_objects(collection, page, recurse, verbosity, url_matcher):
    if verbosity > 0:
        print 'Adding %s to collection' % page.url
    collection.add_object(page)
    if recurse > 0:
        if verbosity > 0:
            print 'Recursing into links of %s' % page.url
        if page.content is None:
            page.read_content()
        for subobj in page.linked_objects():
            if subobj.url in collection.objects:
                subobj = collection.objects[subobj.url]
            if not url_matcher(subobj.url):
                continue
            collect_objects(collection, subobj, recurse-1, verbosity, url_matcher)
  
if __name__ == '__main__':
    main()
