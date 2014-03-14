#!/usr/bin/env python
"""
Finds the closest edit distance between two words, where an edit is an
insert, delete, or letter change.
"""
import time
import sys
import gc

gc.disable()

addone = {}
removeone = {}
editone = {}
dict_filename = '/usr/share/dict/american-english'
dict_length = 98569

class BadCommand(Exception): pass
class NoSolution(Exception): pass

def timeit(desc=None):
    def decorator(func):
        if desc is None:
            actual_desc = func.func_name
        else:
            actual_desc = desc
        def wrapper(*args, **kw):
            start = time.time()
            result = func(*args, **kw)
            finish = time.time()
            print '%s finished in %0.2f sec' % (actual_desc, finish-start)
            return result
        return wrapper
    return decorator

@timeit()
def read_words(verbose=True, addone=addone,
               removeone=removeone, editone=editone):
    global all_words
    read_words = 0
    f = open(dict_filename, 'rb')
    all_words = set(
        line.strip() for line in f if not line.endswith("'s\n"))
    for word in all_words:
        if verbose:
            read_words += 1
            if not read_words % 5000:
                sys.stderr.write('\r%6i / %6i  %2i%%      '
                                 % (read_words, dict_length,
                                    100*read_words/dict_length))
                sys.stderr.flush()
        for i in range(len(word)):
            short = word[:i]+word[i+1:]
            edit = word[:i]+'*'+word[i+1:]
            if short in all_words:
                if short in addone:
                    addone[short][word] = None
                else:
                    addone[short] = {word: None}
            if edit in editone:
                editone[edit][word] = None
            else:
                editone[edit] = {word: None}
    if verbose:
        sys.stderr.write('\rfinished%s\r' % (' '*20))
        sys.stderr.flush()

def neighbors(word):
    all = set()
    # All the words that have one more character:
    if word in addone:
        all.update(addone[word])
    # All the words that are edits of this word (1 char different)
    for i in range(len(word)):
        edit = word[:i]+'*'+word[i+1:]
        all.update(editone[edit])
    # All the words that remove one character:
    for i in range(len(word)):
        short = word[:i]+word[i+1:]
        if short in all_words:
            all.add(short)
    # The word itself will have snuck in:
    all.remove(word)
    return all

@timeit()
def find_word_distance(word1, word2):
    for word in word1, word2:
        if word not in all_words:
            print '%r not found in dictionary' % word
            return
    try:
        path = find_path(word1, word2)
    except NoSolution, e:
        print 'No solution for %s -> %s' % (word1, word2)
        return
    print '%s -> %s length %s' % (word1, word2, len(path))
    for i, arg in enumerate(path):
        assert arg in all_words
        print '  %i %s' % (i+1, arg)

def find_path(word1, word2):
    if word1 == word2:
        return [word1]
    inner, length = find_word_intersect(word1, word2)
    #print 'inner %s->%s->%s length %s' % (word1, inner, word2, length)
    if inner == word1 or inner == word2:
        return [word1, word2]
    return find_path(word1, inner) + find_path(inner, word2)[1:]

def find_word_intersect(word1, word2):
    """returns the intersecting word between the two words,
    and the length"""
    word1_set = set([word1])
    word2_set = set([word2])
    seen = set()
    length = 0
    while 1:
        #print length, word1_set, word2_set
        #print length, seen
        word1_set = extend_set(word1_set, seen)
        length += 1
        if word1_set.intersection(word2_set):
            # We have match!
            break
        #print length, word1_set, word2_set
        #print length, seen
        word2_set = extend_set(word2_set, seen)
        length += 1
        if word2_set.intersection(word1_set):
            # Again!
            break
        if not word1_set or not word2_set:
            raise NoSolution('There is no solution (stuck on %s->%s, depth %s)'
                             % (word1, word2, length))
    inner = word1_set.intersection(word2_set).pop()
    #print 'solution!', word1, inner, word2, length
    return inner, length

def extend_set(word_set, seen):
    new_set = set()
    for word in word_set:
        new_set.update(neighbors(word))
    new_set.difference_update(seen)
    seen.update(word_set)
    return new_set

if __name__ == '__main__':
    words = sys.argv[1:]
    if not words or len(words) % 2:
        print 'Usage: %s word1 word2' % sys.argv[0]
        sys.exit(2)
    try:
        read_words()
        for i in range(len(words)/2):
            find_word_distance(words[i*2], words[i*2+1])
    except BadCommand, e:
        print e
        sys.exit(2)
