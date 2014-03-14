import whitespace
import os

here = os.path.dirname(__file__)
fn = os.path.join(here, 'example_evil_code.py')
fn_out = os.path.join(here, 'example_evil_encoded.py')

content = open(fn, 'rb').read()
print 'encoding', repr(content)
output = content.encode('whitespace')
output = '#coding:whitespace\n' + output
f = open(fn_out, 'wb')
f.write(output)
f.close()
print 'done'
