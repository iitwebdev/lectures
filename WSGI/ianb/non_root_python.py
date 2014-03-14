#!/usr/bin/env python
# From instructions at:
#  http://peak.telecommunity.com/DevCenter/EasyInstall#non-root-installation

import sys
import os
import optparse
import shutil
import urllib

py_version = 'python%s.%s' % (sys.version_info[0], sys.version_info[1])

parser = optparse.OptionParser()
parser.add_option('-v', '--verbose',
                  action='count',
                  dest='verbose',
                  default=0,
                  help="Increase verbosity")
parser.add_option('--lib-dir',
                  dest="lib_dir",
                  default=os.path.expanduser('~/lib/%s' % py_version),
                  help="The non-root library directory to install to (default ~/lib/%s)" % py_version)
parser.add_option('--include-dir',
                  dest="include_dir",
                  default=os.path.expanduser('~/include/%s' % py_version),
                  help="The non-root include directory to install to (default ~/include/%s" % py_version)
parser.add_option('--bin-dir',
                  dest="bin_dir",
                  default=os.path.expanduser('~/bin'),
                  help="The non-root location for your Python executable (default ~/bin)")
parser.add_option('--clear',
                  dest='clear',
                  action='store_true',
                  help="Clear out the non-root install and start from scratch")
parser.add_option('--no-site-packages',
                  dest='no_site_packages',
                  action='store_true',
                  help="Don't copy the contents of the global site-packages dir to the non-root site-packages")
parser.add_option('--svn-setuptools',
                  dest="svn_setuptools",
                  action="store_true",
                  help="Install the SVN version of setuptools")
parser.add_option('--include-package',
                  action='append',
                  dest='include_packages',
                  help="Bring over the named package from site-packages (useful when used with --no-site-packages)")


def mkdir(path):
    if not os.path.exists(path):
        print 'Creating %s' % path
        os.makedirs(path)
    else:
        if verbose:
            print 'Directory %s already exists'

def symlink(src, dest):
    if not os.path.exists(dest):
        if verbose:
            print 'Creating symlink %s' % dest
        os.symlink(src, dest)
    else:
        print 'Symlink %s already exists' % dest

def rmtree(dir):
    if os.path.exists(dir):
        print 'Deleting tree %s' % dir
        shutil.rmtree(dir)
    else:
        if verbose:
            print 'Do not need to delete %s; already gone' % dir

def make_exe(fn):
    if os.name == 'posix':
        oldmode = os.stat(fn).st_mode & 07777
        newmode = (oldmode | 0555) & 07777
        os.chmod(fn, newmode)
        if verbose:
            print 'Changed mode of %s to %s' % (fn, oct(newmode))


join = os.path.join

distutils_cfg_tmpl = """\
[install]
install_lib = ~/lib/python$py_version_short/site-packages
install_scripts = ~/bin

[easy_install]
script_dir = %(bin_dir)s
"""

sitecustomize_tmpl = """\
import sys
for path in sys.path[:]:
    if not path.startswith(sys.prefix):
        sys.path.remove(path)
"""

mypy_tmpl = """\
#!/bin/sh

SCRIPT="$1"
shift
~/bin/python `which "$SCRIPT"` $*
"""

def main():
    options, args = parser.parse_args()
    global verbose
    if sys.executable.startswith(options.bin_dir):
        print 'Error: You should not use the non-root Python executable to run this script'
        return
    verbose = options.verbose
    assert not args, "No arguments allowed"
    lib_dir = options.lib_dir
    if options.clear:
        rmtree(lib_dir)
        rmtree(options.include_dir)
        print 'Not deleting %s' % options.bin_dir
    prefix = sys.prefix
    mkdir(lib_dir)
    stdlib_dir = join(prefix, 'lib', py_version)
    for fn in os.listdir(stdlib_dir):
        if fn in ('site-packages', 'distutils'):
            continue
        symlink(join(stdlib_dir, fn), join(lib_dir, fn))
    mkdir(join(lib_dir, 'site-packages'))
    if not options.no_site_packages:
        for fn in os.listdir(join(stdlib_dir, 'site-packages')):
            symlink(join(stdlib_dir, 'site-packages', fn),
                    join(lib_dir, 'site-packages', fn))
    elif options.include_packages:
        for pkg in options.include_packages:
            any = False
            for ext in ['', '.py', '.so']:
                src = join(stdlib_dir, 'site-packages', pkg + ext)
                if os.path.exists(src):
                    symlink(src, 
                            join(lib_dir, 'site-packages', pkg+ext))
                    any = True
            if not any:
                print 'Warning: could not find package %s' % pkg
    mkdir(join(lib_dir, 'distutils'))
    for fn in os.listdir(join(stdlib_dir, 'distutils')):
        if fn == 'distutils.cfg':
            continue
        symlink(join(stdlib_dir, 'distutils', fn),
                join(lib_dir, 'distutils', fn))
    mkdir(options.include_dir)
    stdinc_dir = join(prefix, 'include', py_version)
    for fn in os.listdir(stdinc_dir):
        symlink(join(stdinc_dir, fn), join(options.include_dir, fn))
    if sys.exec_prefix != sys.prefix:
        exec_dir = join(sys.exec_prefix, 'lib', py_version)
        for fn in os.listdir(exec_dir):
            symlink(join(exec_dir, fn), join(lib_dir, fn))
    mkdir(options.bin_dir)
    print 'Copying %s to %s' % (sys.executable, options.bin_dir)
    py_executable = join(options.bin_dir, 'python')
    if sys.executable != py_executable:
        shutil.copyfile(sys.executable, py_executable)
        make_exe(py_executable)
    pydistutils = os.path.expanduser('~/.pydistutils.cfg')
    distutils_cfg = distutils_cfg_tmpl % {
        'bin_dir': options.bin_dir,
        }
    if os.path.exists(pydistutils):
        print 'Cannot update %s (already exists)' % pydistutils
        print "Add these lines if necessary:"
        print distutils_cfg
    else:
        f = open(pydistutils, 'w')
        f.write(distutils_cfg)
        f.close()
        print "Wrote to %s" % pydistutils
    sitecust = join(lib_dir, 'sitecustomize.py')
    if os.path.exists(sitecust):
        print 'Overwriting %s' % sitecust
        os.unlink(sitecust)
    f = open(sitecust, 'w')
    f.write(sitecustomize_tmpl)
    f.close()
    # @@: I'm not sure if I should do this; removing for now
    if 0:
        mypy = join(options.bin_dir, 'mypy')
        if os.path.exists(mypy):
            print 'Cannot create %s: already exists' % mypy
        else:
            print 'Writing script %s' % mypy
            f = open(mypy, 'w')
            f.write(mypy_tmpl)
            f.close()
            make_exe(mypy)
            print 'Use "mypy script args" to run a script on the system with this'
            print 'local python installation'
    if options.svn_setuptools:
        svn_root = os.path.expanduser('~/svn/')
        mkdir(svn_root)
        setuptools_dir = join(svn_root, 'setuptools')
        if not os.path.exists(setuptools_dir):
            print 'Checking out setuptools to %s' % setuptools_dir
            os.system(
                'cd %s; svn co http://svn.python.org/projects/sandbox/trunk/setuptools'
                % svn_root)
        os.system(
            'cd %s ; %s setup.py develop'
            % (setuptools_dir, py_executable))
    else:
        f = urllib.urlopen('http://peak.telecommunity.com/dist/ez_setup.py')
        fout = open(join(lib_dir, 'ez_setup.py'), 'w')
        fout.write(f.read())
        fout.close()
        f.close()
        print 'Installing setuptools with ez_setup.py'
        os.system(
            '%s %s' % (py_executable, join(lib_dir, 'ez_setup.py')))
        

if __name__ == '__main__':
    main()
    
