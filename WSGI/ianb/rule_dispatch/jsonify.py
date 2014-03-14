# Using RuleDispatch:
import pkg_resources
pkg_resources.require('RuleDispatch==0.5a')
import dispatch
print dispatch.__file__
import sqlobject

@dispatch.generic()
def jsonify(obj):
    """
    Return an object that can be serialized with JSON, i.e., it
    is made up of only lists, dictionaries (with string keys),
    and strings, ints, and floats.
    """
    raise NotImplementedError

@jsonify.when('isinstance(obj, (int, float, str, unicode))')
def jsonify_simple(obj):
    return obj

# @@: Should this match all iterables?
@jsonify.when('isinstance(obj, (list, tuple))')
def jsonify_list(obj):
    return [jsonify(v) for v in obj]

@jsonify.when('isinstance(obj, dict)')
def jsonify_dict(obj):
    result = {}
    for name in obj:
        if not isinstance(name, (str, unicode)):
            raise ValueError(
                "Cannot represent dictionaries with non-string keys in JSON (found: %r)" % name)
        result[name] = jsonify(obj[name])
    return result

@jsonify.when('isinstance(obj, sqlobject.SQLObject)')
def jsonify_sqlobject(obj):
    result = {}
    result['id'] = obj.id
    for name in obj.sqlmeta.columns.keys():
        result[name] = getattr(obj, name)
    return result

@jsonify.when('hasattr(obj, "__json__")')
def jsonify_explicit(obj):
    return obj.__json__()

@jsonify.when('isinstance(obj, sqlobject.SQLObject.SelectResultsClass)')
def jsonify_select_results(obj):
    return jsonify_list(obj)
