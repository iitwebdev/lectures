"""
Test msgpack and json encoding and decoding.  To use, first run this script once to get
some data.  Then:

  python msgpack_json_comparison.py size
  python -m timeit -s 'from msgpack_json_comparison import *' 'json.dumps(data)'
  python -m timeit -s 'from msgpack_json_comparison import *' 'simplejson.dumps(data)'
  python -m timeit -s 'from msgpack_json_comparison import *' 'msgpack.dumps(data)'
  python -m timeit -s 'from msgpack_json_comparison import *' 'json.loads(json_encoded)'
  python -m timeit -s 'from msgpack_json_comparison import *' 'simplejson.loads(json_encoded)'
  python -m timeit -s 'from msgpack_json_comparison import *' 'msgpack.loads(msgpack_encoded)'

"""

from random import randint
import os
import urllib
import simplejson
import json
import msgpack

URL = "http://apps.db.ripe.net/whois/lookup/ripe/inetnum/%s.json"


def make_data(length=100):
    data = []
    while len(data) < length:
        ip = "%s.%s.%s.%s" % (randint(0, 256), randint(0, 256), randint(0, 256), randint(0, 256))
        print ip
        try:
            r = urllib.urlopen(URL % ip)
            data.append(simplejson.load(r))
        except Exception, e:
            print "  skipping (%s)" % e
            pass
    return data

filename = os.path.join(os.path.dirname(__file__), "data.json")
if os.path.exists(filename) and os.path.getsize(filename):
    with open(filename, 'rb') as fp:
        data = json.load(fp)
else:
    with open(filename, 'wb') as fp:
        print "Reading data from net"
        data = make_data()
        print "writing data to %s" % filename
        json.dump(data, fp)

json_encoded = json.dumps(data, separators=(",", ":"))
msgpack_encoded = msgpack.dumps(data)

if __name__ == "__main__":
    import sys
    if "size" in sys.argv:
        print "msgpack size: %i bytes (%i%% of json)" % (
            len(msgpack_encoded), 100.0 * len(msgpack_encoded) / len(json_encoded))
        print "json size:    %i bytes (%i%% of msgpac)" % (
            len(json_encoded), 100.0 * len(json_encoded) / len(msgpack_encoded))
