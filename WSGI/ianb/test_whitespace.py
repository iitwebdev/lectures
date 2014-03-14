import whitespace
import sys

if sys.argv[1:] == ['compile']:
    print "recompiling..."
    f = open('whitespace_source_module.py', 'rb')
    c = f.read()
    f.close()
    c_enc = c.encode('whitespace')
    print 'Encoded %r to %r' % (c, c_enc)
    c_enc = '# -*- encoding: whitespace -*-\n%s' % c_enc
    f = open('whitespace_example_module.py', 'wb')
    f.write(c_enc)
    f.close()
elif sys.argv[1:] == ['display']:
    f = open('whitespace_example_module.py', 'rb')
    c = f.read()
    f.close()
    print 'Encoded: %r' % c
    print 'Decoded: %r' % c.decode('whitespace')
else:
    print 'Running module...'
    import whitespace_example_module

