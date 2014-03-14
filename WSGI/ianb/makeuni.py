__all__ = ['makeuni']
import random

characters = {
    'a': 228,
    'A': 916,
    'e': 603,
    'E': 276,
    'i': 5029,
    'I': 207,
    'o': 4592,
    'O': 10752,
    'u': 3745,
    'U': 1062,
    }

def makeuni(s=None):
    """
    Converts the vowels (AEIOU) in its bytestring input into Unicode
    characters.  This is intended to ease the production of Unicode,
    non-ASCII-encodable strings for test cases.  The string will
    always be transformed in the same way, making it suitable for use
    in doctests or other places.

    If no string is given, then a random string will be produced.
    """
    if s is None:
        s = ''.join([unichr(random.randint(128, 1000)) for i in range(5)])
        return s
    s = unicode(s)
    for c, repl in characters.items():
        s = s.replace(c, unichr(repl))
    return s

