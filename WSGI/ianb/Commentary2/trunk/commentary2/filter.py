from wsgifilter import Filter as WSGIFilter
import re

body_end_re = re.compile(r'</body.*>', re.I)

SCRIPT = '''\
<script type="text/javascript">
if (typeof Commentary == 'undefined') {
    Commentary = {};
}
Commentary.baseURL = '%(base)s';
Commentary.atomBaseURL = '%(base)s/_atompub';
</script>
<script type="text/javascript" src="%(base)s/_commentary/taggerclient/xmlParse.js"></script>
<script type="text/javascript" src="%(base)s/_commentary/taggerclient/atom.js"></script>
<script type="text/javascript" src="%(base)s/_commentary/dumbpath.js"></script>
<script type="text/javascript" src="%(base)s/_commentary/commentary.js"></script>
'''

class Filter(WSGIFilter):

    def __call__(self, environ, start_response):
        environ['commentary2.script_name'] = environ.get('SCRIPT_NAME', '')
        return super(Filter, self).__call__(environ, start_response)
    
    def filter(self, environ, headers, data):
        match = body_end_re.search(data)
        script = SCRIPT % dict(base=environ['commentary2.script_name'])
        if not match:
            data += script
        else:
            data = data[:match.start()]+script+data[match.start():]
        return data

            
