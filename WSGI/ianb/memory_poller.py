import types

class _X(object):
    def y(self): pass

UnboundMethodType = type(_X.y)
BoundMethodType = type(_X().y)

class MemoryProfiler(object):

    def __init__(self, root_object, root_name,
                 module=None, instance_only=True):
        self.root_object = root_object
        self.root_name = root_name
        self.module = module
        self.instance_only = instance_only
        self.seen = {}
        self.paths = {}
        self.sizes = {}

    def scan(self):
        self.poll(self.root_object, (self.root_name,))

    def poll(self, obj, path):
        this_id = id(obj)
        if this_id in self.sizes:
            return 0 # @@ or: self.sizes[this_id] ?
        if this_id in self.seen:
            return 0 # @@: recursion?
        self.seen[this_id] = None
        self.paths[this_id] = path
        size = self.getsize(obj, path)
        self.sizes[this_id] = size
        return size

    def getsize(self, obj, path):
        if (isinstance(obj, types.ModuleType)
            and self.module is not None
            and obj.__name__ != self.module):
            return 0
        if (isinstance(obj, (type, types.ClassType))
            and self.module is not None
            and obj.__module__ != self.module):
            return 0
        if (self.instance_only
            and isinstance(obj, (types.FunctionType, UnboundMethodType, BoundMethodType))):
            return 0
        if isinstance(obj, (str, unicode, int, long)):
            if isinstance(obj, str):
                size = len(obj)
            elif isinstance(obj, unicode):
                size = len(obj.encode('unicode_internal'))
            elif isinstance(obj, int):
                size = 4 # @@ ?
            elif isinstance(obj, long):
                size = 20
            return size
        if hasattr(obj, '__iter__') and hasattr(obj, '__getitem__'):
            size = 4 # @@ ?
            if hasattr(obj, 'items'):
                # Dict object
                try:
                    items = obj.items()
                except TypeError: # Probably a class
                    items = None
                else:
                    for key, value in obj.items():
                        if key in ('__builtins__', '__doc__'):
                            continue
                        key_name = str(key)[:15]
                        size += (self.poll(key, path + ('key:'+key_name,))
                                 + self.poll(value, path + (key_name,)))
            elif hasattr(obj, 'fileno'):
                size = 10
                items = 0
            else:
                try:
                    iterator = iter(obj)
                except TypeError:
                    items = None
                else:
                    items = 0
                    for i, item in enumerate(iterator):
                        size += self.poll(item, path + (str(i),))
            if items is not None:
                return size
        if hasattr(obj, '__dict__'):
            instance = self.poll(obj.__dict__, path)
        else:
            instance = 0
        if hasattr(obj, '__class__'):
            name = 'class:%s' % obj.__class__.__name__
            cls_value = self.poll(obj.__class__, path+(name,))
        else:
            cls_value = 0
        return instance + cls_value + 4

    def report(self, cusp=100):
        paths = sorted(self.paths.iteritems(),
                       key=lambda x: x[1])
        result = []
        for id, path in paths:
            size = self.sizes[id]
            if size < cusp:
                continue
            name = '/'.join(path)
            result.append('%6i %s' % (size, name))
        return '\n'.join(result)

def show_memory(root_object, root_name, cusp=100, module=None):
    mem = MemoryProfiler(root_object, root_name, module)
    mem.scan()
    print mem.report(cusp)

if __name__ == '__main__':
    import sys
    import cgi
    if not sys.argv[1:]:
        show_memory(sys.modules, 'modules')
        sys.exit()
    mod = sys.argv[1]
    if sys.argv[2:]:
        cusp = int(sys.argv[2])
    else:
        cusp = 100
    __import__(mod)
    show_memory(sys.modules[mod], mod, cusp=cusp, module=mod)
