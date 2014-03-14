from jsonify import jsonify
import sqlobject as so

so.sqlhub.processConnection = so.connectionForURI('sqlite:/:memory:')

class Foo(so.SQLObject):
    name = so.StringCol()
    
class Bar(so.SQLObject):

    name = so.StringCol()
    value = so.IntCol()
    foo = so.ForeignKey('Foo')

Foo.createTable()
Bar.createTable()

class Expl:

    def __init__(self, name, *objs):
        self.name = name
        self.objs = objs

    def __json__(self):
        return {
            'name': self.name,
            'objs': [jsonify(o) for o in self.objs]}
    
def test_basic():
    for v in [
        1, 1.0, 'foo', u'bar',
        [1, 2], 
        {'a': 1, 'b': 2}]:
        assert jsonify(v) == v
    assert jsonify((1, 'a', {'b': 2})) == [
        1, 'a', {'b': 2}]

def test_sqlobject():
    f = Foo(name='foo')
    b = Bar(name='bar', value=1, foo=f)
    assert jsonify(f) == {'name': 'foo', 'id': f.id}
    assert jsonify(b) == {'name': 'bar', 'value': 1,
                          'fooID': f.id, 'id': b.id}

def test_explicit():
    e = Expl('foo', 'a')
    result = {'name': 'foo', 'objs': ['a']}
    assert jsonify(e) == result
    assert jsonify([e]) == [result]

class State(so.SQLObject):

    name = so.StringCol()
    abbr = so.StringCol()

State.createTable()

@jsonify.when('isinstance(obj, State)')
def jsonify_state(obj):
    return obj.name

def test_explicit():
    assert jsonify(State(name='Illinois', abbr='IL')) == 'Illinois'
