"""
An alternative to sys.exit, which tries to exit properly, but if that
fails exits more forcefully.  Use thread_die.die(exit_code)
"""

import threading
import time
import os
import sys
import atexit


class DieSoon(threading.Thread):

    def __init__(self, exit_code=0, delay=2):
        threading.Thread.__init__(self)
        self.exit_code = exit_code
        self.delay = delay
        self.exit_event = threading.Event()
        atexit.register(self.set_exit)

    def set_exit(self):
        self.exit_event.set()

    def run(self):
        self.exit_event.wait()
        if not self.zombie_threads():
            return
        time.sleep(self.delay)
        if self.zombie_threads():
            sys.stderr.write(
                "Unclean exit due to zombie threads: %s"
                % (', '.join(map(repr, self.zombie_threads()))))
            os._exit(self.exit_code)

    def zombie_threads(self):
        zombie_threads = []
        for thread in threading.enumerate():
            if thread == self:
                continue
            if thread.getName() == 'MainThread':
                continue
            zombie_threads.append(thread)
        return zombie_threads

def die(exit_code=0):
    t = DieSoon(exit_code=exit_code)
    t.start()
    sys.exit(exit_code)

if __name__ == '__main__':
    def forever():
        while 1:
            time.sleep(1)
            print "going forever..."
    if sys.argv[1:]:
        print "Immediate termination"
    else:
        print "Wedged thread"
        t = threading.Thread(target=forever)
        t.start()
    die()
    
