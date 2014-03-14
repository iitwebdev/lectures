"""
This module can be used to determine what paths should show up in your
sys.path.  This can help with process startup times, especially in a
CGI context (where all modules are loaded for every request).

You might temporarily add it to your CGI script at the very end,
like::

    sys.stderr.write(repr(detect_sys_paths.sys_paths()))

Then use that information to add the lines to the top::

    import sys
    sys.path = [paths...]
"""

import sys

def sys_paths(exclude_unused=1):
    """
    Returns an ordered list of paths that are found in sys.path,
    where early paths are used by more modules.  Paths that are not
    used by any modules will be excluded if exclude_unused is True.
    """
    paths = {}
    for path in sys.path:
        paths[path] = 0
    for module in sys.modules.values():
        if not module:
            continue
        filename = getattr(module, '__file__', None)
        if filename == __file__ or not filename:
            continue
        for path in paths.keys():
            if filename.startswith(path):
                paths[path] += 1
    if exclude_unused:
        for key, value in paths.items():
            if not value:
                del paths[key]
    all = paths.items()
    all.sort(lambda a, b: cmp(-a[1], -b[1]))
    return [path for path, count in all]

