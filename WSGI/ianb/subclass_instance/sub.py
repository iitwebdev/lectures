class Subclassable(object):

    def __init__(self, *args, **kw):
        if args:
            # We're being used as a class!
            name, clone_from_bases, new_attrs = args
            new_attrs['__name__'] = name
            kw = {}
            for clone_from in clone_from_bases:
                kw.update(clone_from.__dict__)
            kw.update(new_attrs)
        print "Creating with %s" % kw
        for name, value in kw.items():
            setattr(self, name, value)

    def __call__(self, **kw):
        new = self.__class__(**self.__dict__)
        for name, value in kw.items():
            setattr(new, name, value)
        return new

    def __repr__(self):
        return '<%s %s>' % (
            getattr(self, '__name__', self.__class__.__name__),
            ' '.join([
            '%s=%r' % (n, v) for n, v in self.__dict__.items()
            if not n.startswith('_')]))
