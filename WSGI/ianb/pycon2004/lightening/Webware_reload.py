from slides import Lecture, NumSlide, Slide, Bullet, SubBullet, PRE, URL, toHTML

class TT:
    tag = 'tt'
    def __init__(self, *texts):
        self.texts = texts
    def toHTML(self):
        return ('<%s>'%self.tag) + "".join(map(toHTML, self.texts)) + ('</%s>\n' % self.tag)

class I(TT):
    tag = 'i'
    


lecture = Lecture(
    "Dealing with stale code",

    Slide("The Problem",
          Bullet("Developers update code"),
          Bullet("In a long-running process, old modules stay in memory after "
                 "their source file has been updated"),
          Bullet("Code has various dependencies -- modules import each other"),
          Bullet("Stale code causes crazy behavior (who among us has not "
                 "pulled out hair as their code has resisted change?)")),
    
    Slide("Clever hacks don't work",
          Bullet("If you reload modules when changes are detected, old references persist"),
          Bullet("Especially references to old classes"),
          Bullet("Which might mean just some instances have stale class references (even worse!)"),
          Bullet("You can't just check modules when they are used through certain mechanisms.  ",
                 "Because those modules depend on other modules, and so on..."),
          Bullet("And sometimes there's non-Python files out there as well (e.g., configuration files)"),
          Bullet("You can fix these, but there's oodles of corner cases"),
          Bullet("Worse, every corner case causes hair-pulling bugs"),
          ),
    
    Slide("Webware's shotgun approach",
          Bullet("Implemented by Jason Hildebrand (", URL("http://peaceworks.ca"), ")"),
          Bullet("Put in a hook to keep track of files being used.",
                 SubBullet(Bullet("you can also manually add files"))),
          Bullet("Poll all files regularly (like every second)",
                 SubBullet(Bullet("Or uses libfam to receive change events instead of polling"))),
          Bullet("When any file has changed, restart the system"),
          Bullet("Look in ",
                 TT("Webware.WebKit.ImportSpy")),
          Bullet("Doesn't have any Webware dependencies"),
          ),
    
    Slide("Webware's shotgun restart",
          Bullet("The application server is started with a shell script:",
                 PRE("""\
retcode=3
while test $retcode -eq 3; do
    /usr/bin/env python $OPTIONS Launch.py ThreadedAppServer $*
    retcode=$?
done
""")),
          Bullet("So we exit with error code 3 when we want to restart"),
          Bullet("Restarts are fast, so by the time you've saved your file and returned to the "
                 "browser, you're all ready"),
          Bullet("No corner cases, no cleverness, It Just Works"),
          ),
    )

lecture.renderHTML("reload_slides", "slide-%d.html", css="slides.css")
