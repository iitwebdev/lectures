class dbstring(object):

    """
    >>> s = dbstring('test')
    >>> s
    <dbstring 'test' % ()>
    >>> s % (1, 'this')
    <dbstring 'test' % (1, 'this')>
    >>> s + dbstring(' test 2') % 1
    <dbstring 'test test 2' % (1,)>
    >>> 'T ' + s
    <dbstring 'T test' % ()>
    """

    def __init__(self, string, params=(), placeholder='%s'):
        self.string = string
        self.params = params
        self.placeholder = placeholder

    def with_placeholder(self, new_placeholder):
        if new_placeholder == self.placeholder:
            return self
        return self.__class__(
            self.string.replace(self.placeholder, new_placeholder),
            self.params, placeholder=new_placeholder)
        
    def __mod__(self, other):
        if not isinstance(other, tuple):
            other = (other,)
        return self.__class__(
            self.string, self.params + other,
            placeholder=self.placeholder)

    __pow__ = __mod__

    def __repr__(self):
        return '<%s %r %% %r>' % (
            self.__class__.__name__, self.string, self.params)

    def __add__(self, other):
        if isinstance(other, dbstring):
            other = other.with_placeholder(self.placeholder)
            params = other.params
            s = other.string
        else:
            params = ()
            s = other
        return self.__class__(
            self.string + s, self.params + params,
            placeholder=self.placeholder)

    def __radd__(self, other):
        if not isinstance(other, (str, unicode)):
            raise TypeError(
                "Cannot add %r to %r" % (type(other), type(self)))
        return self.__class__(
            other + self.string, self.params,
            placeholder=self.placeholder)

class dbliteral(object):

    """
    This can be used like ``sqlrepr()``, so you can do::
    
      >>> v = dbliteral(1)
      >>> v
      <dbliteral 1>
      >>> 'test %s' ** v
      <dbstring 'test %s' % (1,)>

    But sadly we have to use ``**`` instead of ``%``, since there's no
    way to overwrite ``str.__mod__`` (``dbliteral.__rmod__`` will
    never be called).
    """

    def __init__(self, value):
        self.value = value

    def __rpow__(self, other):
        if not isinstance(other, (str, unicode)):
            raise TypeError(
                "Cannot %% %r with %r" % (type(other), type(self)))
        return dbstring(
            other, (self.value,))

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.value)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
