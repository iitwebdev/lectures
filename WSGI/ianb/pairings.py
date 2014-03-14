# Make random pairings of names

import random
import optparse

parser = optparse.OptionParser(usage="""%prog [options] name_list
name_list is a newline-seperated list of names""")
parser.add_option('--times',
                  dest="times",
                  type="int",
                  default=1,
                  help="Number of times to make grouping")
parser.add_option('--size',
                  dest='size',
                  type='int',
                  default='3',
                  help="Size of a group")

def groupby(names, groupsize):
    n = int(len(names) /groupsize)
    groups = [[] for i in range(n)]
    names = names[:]
    while names:
        for i in range(n):
            if names:
                name = random.choice(names)
                groups[i].append(name)
                names.remove(name)
    for i, group in enumerate(groups):
        print "Group %i" % (i+1)
        for name in group:
            print '  %s' % name

def run():
    options, args = parser.parse_args()
    for i in range(options.times):
        print '-'*40
        groupby(filter(None, args[0].splitlines()),
                options.size)

if __name__ == '__main__':
    run()
    
