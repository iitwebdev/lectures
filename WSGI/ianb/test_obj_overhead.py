import time
import itertools

print "creating data"

data = list(enumerate(range(200000)))

print "data loaded"

def access1(row):
    x = row[0]+row[1]+row.a+row.b

def access1_null(row):
    x = row[0]+row[1]+row[0]+row[1]

class flyweight(object):

    def __init__(self, mapper):
        self.mapper = mapper

    def __getitem__(self, item):
        return self.state[item]

    def __getattr__(self, attr):
        return self.state[self.mapper[attr]]

class attrtuple(tuple):

    def __getattr__(self, attr):
        return self[self.mapper[attr]]

class mapped(object):

    def __init__(self, item, mapper):
        self.mapper = mapper
        self.item = item

    def __getitem__(self, item):
        return self.item[item]

    def __getattr__(self, attr):
        return self.item[self.mapper[attr]]

class expl_mapped(list):
    pass

mapping = {'a': 0, 'b': 1}

def null1():
    for obj in data:
        pass

def null2():
    for obj in data:
        access1_null(obj)

def test_flyweight1():
    mapped = flyweight(mapping)
    for obj in data:
        mapped.state = data

def test_flyweight2():
    mapped = flyweight(mapping)
    for obj in data:
        mapped.state = data
        access1(mapped)

def test_attrtuple1():
    class mapped(attrtuple):
        mapper = mapping
    for obj in data:
        obj = mapped(obj)

def test_attrtuple2():
    class mapped(attrtuple):
        mapper = mapping
    for obj in data:
        obj = mapped(obj)
        access1(obj)

def test_mapped1():
    mapping_local = mapping
    for obj in data:
        obj = mapped(obj, mapping_local)

def test_mapped2():
    mapping_local = mapping
    for obj in data:
        obj = mapped(obj, mapping_local)
        access1(obj)

def test_expl_mapping1():
    expl_mapped_local = expl_mapped
    for obj in data:
        mapped = expl_mapped_local(obj)
        mapped.a = obj[0]
        mapped.b = obj[1]

def test_expl_mapping2():
    expl_mapped_local = expl_mapped
    for obj in data:
        mapped = expl_mapped_local(obj)
        mapped.a = obj[0]
        mapped.b = obj[1]
        access1(mapped)

def test_expl_mapping_dict1():
    expl_mapped_local = expl_mapped
    mapping_local = mapping.items()
    for obj in data:
        mapped = expl_mapped_local(obj)
        for name, value in mapping_local:
            setattr(mapped, name, obj[value])

def test_expl_mapping_dict2():
    expl_mapped_local = expl_mapped
    mapping_local = mapping.items()
    for obj in data:
        mapped = expl_mapped_local(obj)
        for name, value in mapping_local:
            setattr(mapped, name, obj[value])
        access1(mapped)

def timeit(func, standard=None):
    least = None
    clock = time.clock
    for i in range(3):
        start = clock()
        func()
        end = clock()
        if least is None or least > end-start:
            least = end-start
    if standard is not None:
        mult = least / standard
        mult = ' x%0.1f' % mult
    else:
        mult = ''
    print "Time for %s: %f seconds%s" % (func.func_name, least, mult)
    return least

std1 = timeit(null1)
std2 = timeit(null2)
for name, value in sorted(globals().items()):
    if name.startswith('test_'):
        if name.endswith('1'):
            timeit(value, std1)
        else:
            timeit(value, std2)
