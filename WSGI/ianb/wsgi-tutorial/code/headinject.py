import re
from filter import HTMLFilter

class HeadInject(HTMLFilter):

    def __init__(self, app, extra_head):
        super(HeadInject, self).__init__(app)
        self.extra_head = extra_head

    def filter(self, script_name, path_info, environ,
               status, headers, body):
        match = re.search(r'</head>', body, re.IGNORECASE)
        if match:
            start, rest = body[:match.start()], body[match.start():]
        else:
            start, rest = body, ''
        body = (start
                + self.extra_head
                + rest)
        return status, headers, body
    
