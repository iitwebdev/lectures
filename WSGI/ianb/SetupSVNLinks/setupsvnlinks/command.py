import sys
import os
import urlparse
import subprocess
import cgi
from paste.util.template import HTMLTemplate
from cmdutils import OptionParser, CommandError, main_func
from fnmatch import fnmatch

## The long description of how this command works:
description = """\
Create an HTML file (on stdout) linking to all the tags and branches
and trunk in all the repositories, with links that easy_install
understands.

Repository URLs can contain * wildcards.
"""

parser = OptionParser(
    version_package='SetupSVNLinks',
    usage="%prog [OPTIONS] REPOS...",
    description=description,
    min_args=1,
    ## Set this to true to create a logger:
    #use_logging=False,
    )

parser.add_option(
    '--base',
    action="store",
    dest="repo_base",
    help="Base URL for all the repositories")

parser.add_option(
    '--header',
    dest="header",
    metavar="FILENAME",
    help="Header for the output")

parser.add_option(
    '--footer',
    dest="footer",
    metavar="FILENAME",
    help="Footer for the output")

parser.add_option(
    '--template',
    dest='template',
    metavar='FILENAME',
    help="Paste template for the output")

def get_file(filename):
    if not filename or not os.path.exists(filename):
        return ''
    f = open(filename, 'rb')
    try:
        return f.read()
    finally:
        f.close()

@main_func(parser)
def main(options, args):
    repos = args
    if options.repo_base:
        if not options.repo_base.endswith('/'):
            options.repo_base += '/'
        repos = [
            urlparse.urljoin(options.repo_base, repo)
            for repo in repos]
    new_repos = []
    for repo in repos:
        new_repos.extend(patmatch_repos(repo))
    repos = new_repos
    links = make_links(repos)
    footer = get_file(options.footer)
    header = get_file(options.header)
    tmpl_filename = (
        options.template
        or os.path.join(os.path.dirname(__file__), 'output_template.html_tmpl'))
    template = HTMLTemplate.from_filename(tmpl_filename)
    vars = {
        'links': links,
        'footer': footer,
        'header': header,
        }
    print template.substitute(vars)

def join(base_url, path, fragment=None):
    if not base_url.endswith('/'):
        base_url += '/'
    result = urlparse.urljoin(base_url, path)
    if fragment:
        result += '#' + fragment
    return result

def make_links(repos):
    links = []
    for repo in repos:
        for link in find_links(repo):
            if link not in links:
                links.append(link)
    return links

def get_output(*args):
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE)
    output = proc.communicate()[0]
    return output

def lines(s):
    return [
        line.strip() for line in s.splitlines()
        if line.strip()]

def find_links(repo):
    package = detect_package(repo)
    yield join(repo, 'trunk', 'egg=%s-dev' % package)
    tag_url = join(repo, 'tags/')
    for line in lines(get_output('svn', 'ls', tag_url)):
        line = line.strip('/')
        yield join(tag_url, line, 'egg=%s-%s' % (package, line))

def detect_package(repo):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(repo)
    path = path.rstrip('/')
    if path:
        parts = path.split('/')
        name = parts[-1]
        if name and name.lower() != 'svn':
            return name
    parts = netloc.lower().split('.')
    while parts and parts[0] == 'svn':
        parts.pop(0)
    if not parts:
        raise Exception(
            "Cannot determine package name from %s" % repo)
    return parts[0]

def patmatch_repos(repo):
    repo = repo.rstrip('/')
    if '*' in repo.split('/')[-1]:
        pattern = repo.split('/')[-1]
        results = []
        for line in lines(get_output('svn', 'ls', repo.rstrip('*'))):
            if fnmatch(line, pattern):
                results.append(urlparse.urljoin(repo, line))
        return results
    elif '*' in repo:
        raise CommandError('Cannot resolve wildcard in repository %r' % repo)
    else:
        return [repo]
        
        
    
if __name__ == '__main__':
    main()
