#From: http://howithappened.com/2007/09/three-way-pistol-duel-puzzle.html
import random

def run(choose):
    living = dict(me=True, bad=True, good=True)
    probs = dict(me=.33, bad=.5, good=1)
    order = ['me', 'bad', 'good']
    def shoot(player, target):
        print 'Player %s fires at %s' % (player, target)
        if random.random() < probs[player]:
            print '  HIT!'
            living[target] = False
        else:
            print '  miss'
    def living_count():
        return len(filter(None, living.values()))
    while 1:
        if living_count() == 1:
            print 'The fight is over'
            for key, value in living.items():
                if value:
                    print 'The survivor is: %s' % key
                    print '-'*60
                    return key
            break
        for shooter in order:
            if not living[shooter]:
                print 'Shooter %s is dead' % shooter
                continue
            if shooter == 'me':
                if living_count() == 3:
                    if choose is None:
                        print 'You shoot at no one'
                        continue
                    else:
                        target = choose
                else:
                    if living['good']:
                        target = 'good'
                    else:
                        target = 'bad'
            elif shooter == 'good':
                if living['bad']:
                    target = 'bad'
                else:
                    target = 'me'
            else:
                if living['good']:
                    target = 'good'
                else:
                    target = 'me'
            shoot(shooter, target)

if __name__ == '__main__':
    import sys
    from cStringIO import StringIO
    args = sys.argv[1:]
    if not args:
        print 'Usage: %s [-q] COUNT me/bad/good'
    if args[0] == '-q':
        quiet = True
        args.pop(0)
    for choose in args[1:]:
        winners = dict(me=0, bad=0, good=0)
        count = int(args[0])
        if choose.lower() == 'none':
            choose = None
        for i in xrange(count):
            if quiet:
                sys.stdout = StringIO()
            winner = run(choose)
            winners[winner] += 1
        sys.stdout = sys.__stdout__
        print "Summary (choose=%s):" % choose
        for key, value in sorted(winners.items()):
            print '  %s: %s' % (key, value)
        print 'Quality: %.1f%%' % (100.0*winners['me']/count)
