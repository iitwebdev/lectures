from slides import Lecture, NumSlide, Slide, Bullet, SubBullet, PRE, URL, toHTML

lecture = Lecture(
    "PyLogo: the Logo Language implemented in Python",

    Slide(
    "PyLogo",
    Bullet("Website: <b><tt>http://pylogo.org</tt></b>"),
    Bullet("Logo is an educational language targeted at young children"),
    Bullet("Logo isn't about teaching programming, but about teaching mathematical ideas "
           "using programming"),
    Bullet("PyLogo is a Logo interpreter written in Python"),
    ),

    Slide(
    "Why Logo?",
    Bullet("Most people don't need the skills to become professional programmers"),
    Bullet("Especially when they are 9 years old"),
    Bullet("We shouldn't confuse our ideas about programming with the education "
           "goals of programming"),
    ),

    Slide(
    "How Logo is different from Python",
    Bullet("It doesn't put effort into code reuse"),
    Bullet("Commands can be abbreviated, and can be very short, "
           "because children type very, very slowly"),
    Bullet("Very little punctuation"),
    Bullet("Structure is casual with respect to command separation and "
           "whitespace, also case-insensitive"),
    Bullet("It uses dynamic typing"),
    ),

    Slide(
    "Examples",
    PRE('''\
? REPEAT 4 [FD 100 RT 90]
? PR [Hello world!]
Hello world!
'''),
           "The Python equivalent:",
    PRE("""\
>>> from turtle import *
>>> for i in range(4):
...     forward(100)
...     right(90)
>>> print 'Hello world!'
Hello world!
""")),

    Slide(
    "What's neat about PyLogo",
    Bullet("It's free, of course (and cross-platform and everything else you get from "
           "implementing it in Python)"),
    Bullet("It's traditional Logo (lots of naive non-traditional implementations of "
           "logo exist)"),
    Bullet("It integrates well with Python")),

    Slide(
    "Python Integration",
    Bullet("All Python functions are made easily available"),
    Bullet("Procedures can be easily annotated with function attributes, "
           "allowing renaming, or allowing access to the Logo interpreter "
           "object."),
    Bullet("Making a procedure available is easy:"),
    PRE("""\
# in turtle.py...
from turtle import forward
forward.aliases = ['fd']
"""),
    PRE('''\
; In logo...
? import "turtle
? FD 100
''')),

    Slide(
    "Integration Example 2",
    Bullet("Even control structures are easy:"),
    PRE("""\
def logoWhile(interp, test, block):
    lastVal = None
    try:
        while logoEval(interp, test):
            try:
                lastVal = logoEval(interp, block)
            except LogoContinue:
                pass
    except LogoBreak:
        lastVal = None
        pass
    return lastVal
logoWhile.logoAware = 1
logoWhile.logoName = 'while'
""")),

    Slide(
    "Why you might want to work on PyLogo",
    Bullet("Python has a bunch of libraries that would be nice to make available "
           "to a Logo user"),
    Bullet("The PyLogo interpreter is really easy to play with (Logo is a <i>very</i> "
           " simple language)"),
    Bullet("Unfortunately, I get really distracted with different projects, so I "
           "haven't been able to keep moving it forward."),
    Bullet("Also, I'm not very experienced with GUI programming, and a Logo environment "
           "should have a good interface"),
    Bullet("But PyLogo has almost no professional potential, so it's just plain "
           "fun"),
    Bullet("Writing languages is fun.  But hard.  Playing around with a toy language "
           "is educational, but ultimately not useful for anyone else."),
    Bullet("But Logo is a toy language that isn't just a toy!"),
    Bullet("Reminder: <b><tt>http://pylogo.org</tt></b>"),
    ))

lecture.renderHTML("logo_slides", "slide-%d.html", css="slides.css")
