#!/usr/bin/env python

import zipfile
import sys
import os
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import smtplib
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.MIMEMultipart import MIMEMultipart
from email import Encoders
import time
import optparse

parser = optparse.OptionParser(usage="%prog [options] <to-email> DIRS...")
parser.add_option('--smtp-server',
                  dest='smtp_server',
                  default='localhost',
                  help="SMTP server to use")
parser.add_option('--max-size',
                  dest='max_size',
                  default=5,
                  help="Maximum size (in Mb) to send (before compression)")
parser.add_option('--from',
                  dest='from_address',
                  help="From address (default to To address)")

def write_dirs(dirs, max_size):
    f = StringIO()
    z = zipfile.ZipFile(f, 'w')
    files = []
    size = 0
    for write_to, fn in enumerate_dirs(dirs):
        size += os.stat(fn).st_size
        if size > max_size:
            z.close()
            yield files, f.getvalue()
            files = []
            f = StringIO()
            z = zipfile.ZipFile(f, 'w')
            size = os.stat(fn).st_size
        if write_to.startswith('.'+os.path.sep):
            write_to = write_to[2:]
        elif write_to.startswith('..'+os.path.sep):
            write_to = write_to[3:]
        z.write(fn, write_to)
        files.append(fn)
    z.close()
    yield files, f.getvalue()

def enumerate_dirs(dirs):
    for dir in dirs:
        base = os.path.basename(dir)
        for val in enumerate_dir(dir, base):
            yield val

def enumerate_dir(dir, base):
    for fn in os.listdir(dir):
        full = os.path.join(dir, fn)
        part = os.path.join(base, fn)
        if os.path.isdir(full):
            for val in enumerate_dir(full, part):
                yield val
        else:
            yield part, full

def send_zip(from_address, to_address, smtp_server, content,
             files, number):
    outer = MIMEMultipart()
    outer['Subject'] = 'Backup from %s (no %i)' % (
        time.strftime('%c'), number)
    outer['To'] = to_address
    outer['From'] = from_address
    desc = MIMEText('Files contained in this zip file:\n\n%s'
                    % '\n'.join(files), _subtype='plain')
    outer.attach(desc)
    inner = MIMEBase('application', 'zip')
    inner.set_payload(content)
    inner.add_header('Content-Disposition', 'attachment',
                     filename=time.strftime('backup-%%i%Y-%m-%d.zip')%number)
    outer.attach(inner)
    Encoders.encode_base64(inner)
    print '%.1fMb in zip %i' % (len(content)/1000000.0, number)
    sys.stdout.write('Sending to %s (via %s)...' % (to_address, smtp_server))
    sys.stdout.flush()
    server = smtplib.SMTP(smtp_server)
    server.sendmail(from_address, [to_address], outer.as_string())
    server.quit()
    sys.stdout.write('done.\n')
    sys.stdout.flush()

def run():
    options, args = parser.parse_args()
    email = args[0]
    dirs = args[1:]
    max_size = int(options.max_size)*1000000
    if not options.from_address:
        options.from_address = email
    for number, (files, zip) in enumerate(write_dirs(dirs, max_size)):
        send_zip(
            options.from_address,
            email,
            options.smtp_server,
            zip, files, number+1)
    print 'Complete.'

if __name__ == '__main__':
    run()
