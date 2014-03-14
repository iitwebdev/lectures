#!/usr/bin/env python

import doctest
import os

def do_tests():
    here = os.path.dirname(__file__)
    for fn in os.listdir(here):
        if fn.endswith('.txt'):
            doctest.testfile(fn, optionflags=
                             doctest.ELLIPSIS
                             | doctest.REPORT_ONLY_FIRST_FAILURE)

if __name__ == '__main__':
    do_tests()
    


