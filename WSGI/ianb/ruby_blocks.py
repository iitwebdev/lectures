#!/usr/bin/env python2.4
"""
A basic example of the technique::

    >>> s = [1, 2, 3]
    >>> @s.sort
    ... def _(a, b):
    ...     return cmp(b, a)
    >>> s
    [3, 2, 1]
"""
import inspect
import types

def foreach(sequence):
    """
    Like Ruby's .each::

        >>> s = [1, 2, 3]
        >>> @foreach(s)
        ... def _(item):
        ...     print item
        1
        2
        3
        
    """
    def decorator(func):
        for item in sequence:
            func(item)
    return decorator

def inject(sequence, start):
    """
    Like Ruby's .inject::

        >>> s = [1, 2, 3]
        >>> @inject(s, 0)
        ... def result(current, item):
        ...     return current + item ** 2
        >>> result
        14
    """
    # Because of scope weirdness, we can't reassign start, so this
    # is a workaround:
    result = [start]
    def decorator(func):
        for item in sequence:
            result[0] = func(result[0], item)
        return result[0]
    return decorator

def collect(sequence):
    """
    Like Ruby's .collect::

        >>> @collect([1, 2, 3])
        ... def result(item):
        ...     return -item
        >>> result
        [-1, -2, -3]
    """
    def decorator(func):
        return [func(item) for item in sequence]
    return decorator

def file_do(filename, mode='r'):
    """
    Like Ruby's file's .do::

        >>> @file_do('ruby_blocks.py')
        ... def _(file):
        ...     print file.readline(),
        #!/usr/bin/env python2.4
    """
    def decorator(func):
        try:
            f = open(filename, mode)
            return func(f)
        finally:
            f.close()
    return decorator

def set(obj, make_method=False):
    """
    Allows you to add a method/function to an object (it's a method
    if you add it to a class, otherwise it's just a function and
    'self' is not bound).  Example::

        >>> class color:
        ...     def __init__(self, r, g, b):
        ...         self.r, self.g, self.b = r, g, b
        >>> c = color(1, 0, 0)
        >>> c      # doctest: +ELLIPSIS
        <__main__.color instance at ...>
        >>> @set(color)
        ... def __repr__(self):
        ...     return '<color %s %s %s>' % (self.r, self.g, self.b)
        >>> c
        <color 1 0 0>
        >>> @set(c)
        ... def printme(self):
        ...     print self
        >>> c.printme()
        Traceback (most recent call last):
            ...
        TypeError: printme() takes exactly 1 argument (0 given)
        >>> c.printme(0)
        0
        >>> @set(c, True)
        ... def printme(self):
        ...     print self
        >>> c.printme()
        <color 1 0 0>
        >>> c.printme(0)
        Traceback (most recent call last):
            ...
        TypeError: printme() takes exactly 1 argument (2 given)
    """
    if make_method:
        def decorator(func):
            def replacement(*args, **kw):
                return func(obj, *args, **kw)
            try:
                replacement.func_name = func.func_name
            except: # @@ except what?  I know it can fail sometimes
                pass
            setattr(obj, func.func_name, replacement)
            return replacement
    else:
        def decorator(func):
            setattr(obj, func.func_name, func)
            return func
    return decorator

def magic_set(obj):
    """
    Adds a function/method to an object.  Uses the name of the first
    argument as a hint about whether it is a method (``self``), class
    method (``cls`` or ``klass``), or static method (anything else).
    Works on both instances and classes.

        >>> class color:
        ...     def __init__(self, r, g, b):
        ...         self.r, self.g, self.b = r, g, b
        >>> c = color(0, 1, 0)
        >>> c      # doctest: +ELLIPSIS
        <__main__.color instance at ...>
        >>> @magic_set(color)
        ... def __repr__(self):
        ...     return '<color %s %s %s>' % (self.r, self.g, self.b)
        >>> c
        <color 0 1 0>
        >>> @magic_set(color)
        ... def red(cls):
        ...     return cls(1, 0, 0)
        >>> color.red()
        <color 1 0 0>
        >>> c.red()
        <color 1 0 0>
        >>> @magic_set(color)
        ... def name():
        ...     return 'color'
        >>> color.name()
        'color'
        >>> @magic_set(c)
        ... def name(self):
        ...     return 'red'
        >>> c.name()
        'red'
        >>> @magic_set(c)
        ... def name(cls):
        ...     return cls.__name__
        >>> c.name()
        'color'
        >>> @magic_set(c)
        ... def pr(obj):
        ...     print obj
        >>> c.pr(1)
        1
    """
    def decorator(func):
        is_class = (isinstance(obj, type)
                    or isinstance(obj, types.ClassType))
        args, varargs, varkw, defaults = inspect.getargspec(func)
        if not args or args[0] not in ('self', 'cls', 'klass'):
            # Static function/method
            if is_class:
                replacement = staticmethod(func)
            else:
                replacement = func
        elif args[0] == 'self':
            if is_class:
                replacement = func
            else:
                def replacement(*args, **kw):
                    return func(obj, *args, **kw)
                try:
                    replacement.func_name = func.func_name
                except:
                    pass
        else:
            if is_class:
                replacement = classmethod(func)
            else:
                def replacement(*args, **kw):
                    return func(obj.__class__, *args, **kw)
                try:
                    replacement.func_name = func.func_name
                except:
                    pass
        setattr(obj, func.func_name, replacement)
        return replacement
    return decorator
        
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
