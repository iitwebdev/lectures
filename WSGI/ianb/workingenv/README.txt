workingenv.py
=============

.. contents::

Installation
------------

You don't need to install this as a Python package; you can simply
`download the script
<http://svn.colorstudy.com/home/ianb/workingenv/workingenv.py>`_ and
run it.  This avoids a chicken-and-egg problem of installing stuff
into your environment so you can start setting up environments.

You can also install it with ``easy_install workingenv.py``, install
it without setuptools (it does not depend on setuptools for
installation), or install from the `subversion repository
<http://svn.colorstudy.com/home/ianb/workingenv/#egg=workingenv.py-dev>`_
with ``easy_install workingenv.py==dev``.

Summary
-------

This tool creates an environment that is isolated from the rest of the
Python installation, eliminating site-packages and any other source of
modules, so that only the modules (and versions) you install into the
environment will be available.  This allows for isolated and
controlled environments, as well as reproduceability.  This is similar
to `virtual-python
<http://peak.telecommunity.com/dist/virtual-python.py>`_, but without
the symlinks and with some additional features.

The basic usage is::

    $ python workingenv.py MyNewEnvironment
    $ source MyNewEnvironment/bin/activate

After sourcing ``bin/activate`` any commands (like ``python setup.py
install``, etc) will install into the new environment.  A Windows
``activate.bat`` file is also generated for that environment.  Scripts
like ``bin/easy_install`` will be tied to the environment, and so they
will automatically install into the environment even without
activation.

Changes
-------

**0.6.6**: Properly read return code of easy_install commands, so that
failed ``-requirements`` setups don't look successful.  New option
``--log-file``, which will save a verbose log of what workingenv did.

**0.6.5**: Export ``$_WE_OLD_WORKING_PATH``, etc.  Also deactivate
environments when activating a new environment.  Include the Darwin
Ports ``site-packages`` directory on that platform.  ``-env`` was
being totally ignored; working now.

**0.6.4**: Use ``--always-unzip`` with ``ez_setup.py``, so we don't
sometimes (on Python 2.5?) get setuptools installed as an egg.  Don't
put quotes around environmental variables in ``activate.bat``.  Print
out installation with nesting to show what dependencies are drawn in
by what libraries.

**0.6.3**: Don't raise an exception when ``cli|gui.exe`` is missing.
Set ``always_copy = True`` in ``distutils.cfg``, which avoids some
problems with system-wide packages.  Show some indication of progress
during the Setuptools installation.

**0.6.2**: User the system distutils.cfg as well as the
workingenv-specific distutils.cfg; helpful for picking up system-wide
compiler settings.  Fix problem with creating command-line scripts on
Windows (missing ``cli.exe`` or ``gui.exe``).

**0.6.1**: Minor bugfix, plus Windows activate.bat file now changes
the prompt (from Patrick O'Brien).  Also, install script as just
``workingenv`` so it doesn't conflict with the module.

**0.6**: Pulls in dependencies from --requirements files, irregardless of
whether a currently activated environment might provide those
dependencies.  Includes a ``setup.py`` file.  Doesn't print out boring
messages from ``ez_setup.py`` and ``easy_install``.

**0.5**: Fix the self-activation of scripts.

**0.4**: Fix the interaction of the ``--site-packages`` option (that
brings in the global ``site-packages/`` directory) and a global
installation of setuptools.  If you get an error like "site.py is not
a setuptools-generated site.py; please remove it" you should upgrade
and regenerate your workingenv.

**0.3**: Support for Setuptools 0.6c5

Activation
----------

When you "activate" the environment, ``python`` will treat that
environment as though it was the only Python environment available.
It does this by setting ``$PYTHONPATH`` and overriding the standard
``site.py``.

Installations with "setup.py install" and easy_install will go into
the right place.  Scripts built with easy_install (*not other ways*)
will be tied to the environment, even if the environment isn't
activated when the script is run.

Activation itself means putting ``lib/python2.4/`` onto
``$PYTHONPATH``.  If you don't want to use ``bin/activate``, just do:

    $ export PYTHONPATH="WORKINGENV/lib/python2.4"
    $ <anything using Python>

``bin/activate`` also updates your prompt and sets ``$PATH`` to point
to the workingenv ``bin/``.  There is no other magic to it, so you can
reproduce the same functionality that way if you want.  (Note also
that ``bin/activate`` changes your environment, which is why it must
be ``source``\ d into a shell environment.)

See `this post <http://blog.ianbicking.org/working-env.html>`_ for an
initial discussion.  Discussion should go to `distutils-sig@python.org
<http://www.python.org/community/sigs/current/distutils-sig/>`_.

Requirements
------------

Also included is the notion of a requirement set, so you can bootstrap
a complete set of packages.  This is a text file with
``easy_install``\ able requirements, one on each line.  The file can
also include ``-r other_file`` and ``-f place_to_find_packages``.
Using this you can provide a very specific working set of packages for
users/developers.  You may also use ``-e`` before a requirement to
install that requirement into ``src/`` in development mode.

Two examples of this sense of requirements are provided,
"tg-example.txt" and "tg-0.9.txt".  Note that by putting this into a
separate file, adjusting the requirements in response to testing does
not require changing the requirements of any particular package.  This
way you can give very exacting requirements, and later adjust those
requirements in response to upgrades, without causing instabilities in
any one package.

Regenerating Environments
-------------------------

Environments carry around the settings they were created with (in
``.workingenv/``).  This allows you to run ``workingenv.py
ENVIRONMENT`` over again to make updates, and settings will still be
preserved.

Before overwriting any files you will be asked about the changes.
Also you can use ``--simulate`` to see what it *would* do.

Windows
-------

workingenv should work on Windows, but you must use ``activate.bat``
before starting scripts -- they can't self-activate on Windows.

Zope
----

workingenv.py *will* work with Zope 2, but you should use the --home
option (which will put everything in lib/python/ instead of
lib/python2.4/).  The way Zope and many Zope Products are set up, they
expect this kind of layout.

Using workingenv Programmatically
---------------------------------

You can use ``workingenv.main()`` just like the script; this is
probably the best/safest way to use it programmatically.  Of course
calling it in a subprocess will also work.

