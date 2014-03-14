#!/usr/bin/env python

import pyid3lib
from ogg.vorbis import VorbisFile
from path import path
import shutil
import re
import os
import optparse
import sys

default_out_dir = '/home/ianb/music/artist'
default_down_dir = '/home/ianb/music/downsample'

parser = optparse.OptionParser()
parser.add_option(
    '-u', '--update',
    action="store_true",
    dest="update",
    help="Command: Update metadata from filename")
parser.add_option(
    '-m', '--move',
    action="store_true",
    dest="move",
    help="Command: Move file based on metadata")
parser.add_option(
    '--copy',
    action="store_true",
    dest="copy",
    help="Copy files instead of moving them")
parser.add_option(
    '-d', '--downsample',
    action="store_true",
    dest="downsample",
    help="Command: Downsample files")
parser.add_option(
    '-o', '--out',
    metavar='DIR',
    dest="out_dir",
    default=default_out_dir,
    help="Root directory to put files into (default %s)" % default_out_dir)
parser.add_option(
    '-D', '--downsample-dir',
    metavar="DIR",
    dest="down_dir",
    default=default_down_dir,
    help="Root directory for downsampled files (default %s)" % default_down_dir)
parser.add_option(
    '-n', '--simulate',
    action="store_true",
    dest="simulate",
    help="Don't actually write/move files")
parser.add_option(
    '-v', '--verbose',
    action="count",
    dest="verbosity",
    help="Be verbose")

class BadFile(Exception):
    pass

def info_from_filename(filename):
    """
    >>> _prdict(info_from_filename(path('art - alb - 03 - titl.mp3')))
    [('album', 'alb'), ('artist', 'art'), ('encoding', 'mp3'), ('title', 'titl'), ('track', 3)]
    """
    data = {}
    if filename.ext == '.mp3':
        data['encoding'] = 'mp3'
    elif filename.ext == '.ogg':
        data['encoding'] = 'ogg'
    else:
        raise BadFile("Unknown encoding: %r" % filename.ext)

    #filename = unicode(filename.splitext()[0].name, 'iso-8859-1')
    filename = filename.splitext()[0].name
    pieces = map(clean_filename, filename.split(' - '))
    if len(pieces) >= 4:
        data['artist'], data['album'], data['track'] = pieces[:3]
        data['title'] = ' - '.join(pieces[3:])
    elif len(pieces) == 3:
        data['artist'], data['track'], data['title'] = pieces
        try:
            data['track'] = int(data['track'])
            data['album'] = None
        except ValueError:
            data['album'] = data['track']
            data['track'] = None
    elif len(pieces) == 2:
        data['artist'], data['title'] = pieces
        data['track'] = data['album'] = None
    else:
        raise BadFile("Unparsable filename: %r (split to %s)" % (filename, pieces))

    if data['track']:
        try:
            data['track'] = int(data['track'])
        except:
            print "Bad filename: %s" % filename
            raise
    return data

def clean_filename(part):
    for c, repl in [('_', ' '),
                    (' - ', '-'),
                    ('- ', '-'),
                    (' -', '-')]:
        part = part.replace(c, repl)
    return part

def info_from_file(filename):
    if filename.endswith('.mp3'):
        return info_from_mp3(filename)
    elif filename.endswith('.ogg'):
        return info_from_ogg(filename)
    else:
        assert 0, "Unknown file type: %r" % filename

def info_from_mp3(filename):
    try:
        tags = pyid3lib.tag(filename)
        try:
            track = tags.track
        except AttributeError:
            track = find_track(filename)
        return {
            'artist': getattr(tags, 'artist', None),
            'album': getattr(tags, 'album', None),
            'track': track,
            'title': getattr(tags, 'title', None),
            'encoding': 'mp3',
            }
    except AttributeError, e:
        raise BadFile, str(e)

def info_from_ogg(filename):
    vf = VorbisFile(filename)
    vc = vf.comment()
    # We lack track information...
    try:
        data = info_from_filename(filename)
    except BadFile:
        data = {}
        data['track'] = find_track(filename)
    for key in ['artist', 'title', 'album']:
        data[key] = _get_tag(vc, key)
    data['encoding'] = 'ogg'
    return data

def _get_tag(vc, name):
    try:
        return vc[name.upper()][0]
    except KeyError:
        return None

def set_info(filename, data):
    cur = info_from_file(filename)
    updating = []
    for key in ['artist', 'title', 'album', 'track']:
        if data.get(key) is None:
            continue
        if cur[key] is None:
            if data[key]:
                updating.append((key, cur[key], data[key]))
            continue
        if cur[key] != data[key] \
               and clean(cur[key]) != data[key]:
            updating.append((key, cur[key], data[key]))
    if not updating:
        #if DISPLAY:
        #    print "Metadata correct in %s" % filename.name
        return
    if DISPLAY:
        print "Updating %s:\n  %s" % (
            filename.name,
            '\n  '.join(['%s: %s->%s' % u for u in updating]))
    if TESTING:
        return
    if filename.endswith('.mp3'):
        set_info_mp3(filename, updating, data)
    elif filename.endswith('.ogg'):
        set_info_ogg(filename, updating, data)
    else:
        assert 0, "Unknown file type: %r" % filename

def set_info_mp3(filename, updating, data):
    tags = pyid3lib.tag(filename)
    for key, before, after in updating:
        setattr(tags, key, data[key])
    tags.update()

def set_info_ogg(filename, updating, data):
    vf = VorbisFile(filename)
    vc = vf.comment()
    #raise BadFile('track' not in updating, "Cannot update track in ogg file")
    old = vc.items()
    vc.clear()
    keys_updating = [u[0] for u in updating]
    for key, value in old:
        if key.lower() not in keys_updating:
            vc.add_tag(key, value)
    for key in keys_updating:
        vc.add_tag(key.upper(), data[key])
    vc.write_to(filename)

def filename_from_info(data):
    data = data.copy()
    dir_parts = []
    parts = []
    if not data.get('artist'):
        dir_parts.append('Compilation')
        parts.append('Unknown')
    else:
        artist_part = clean(data['artist'])
        if '&' in artist_part:
            artist_part = artist_part.split('&')[0]
        if ',' in artist_part:
            artist_part = artist_part.split(',')[0]
        if artist_part.lower().startswith('the ') and artist_part.lower() != 'the the':
            artist_part = artist_part[4:]
        artist_part = artist_part.strip()
        if artist_part.lower().startswith('the '):
            artist_part = artist_part[4:].strip()
        dir_parts.append(artist_part)
        parts.append(clean(data['artist']))
    if not data.get('album'):
        dir_parts.append('misc')
    else:
        dir_parts.append(clean(data['album']))
        parts.append(clean(data['album']))
    if data.get('track'):
        if isinstance(data['track'], tuple):
            if len(data['track']) == 2:
                parts.append('%02i of %02i' % data['track'])
            else:
                parts.append('%02i' % data['track'])
        else:
            parts.append('%02i' % data['track'])
    if data.get('title'):
        parts.append(clean(data['title']))
    else:
        parts.append('Unknown')
    dir = '/'.join(dir_parts)
    filename = ' - '.join(parts)
    while filename.endswith('.'):
        filename = filename[:-1]
    return path(dir + '/' + filename + '.' + data['encoding'])

def update_from_filename(filename):
    data = info_from_filename(filename)
    for key, value in data.items():
        if not value:
            del data[key]
    set_info(filename, data)

def update_from_metadata(filename, copy=False):
    new = filename_from_info(info_from_file(filename))
    new = out_dir / new
    if new.abspath() == filename.abspath():
        return
    if DISPLAY:
        print '>> %s\n   %s' % (filename, new)
    if not TESTING:
        if not new.parent.exists():
            new.parent.makedirs()
        if copy:
            filename.copy(new)
        else:
            filename.move(new)
        new.chmod(0644)
        trim_dir(filename.abspath().parent)

def trim_dir(dir):
    if dir.abspath() == os.getcwd():
        return
    if not dir.listdir():
        if DISPLAY:
            print 'Trimming directory %s' % dir
        dir.rmdir()
        trim_dir(dir.abspath().parent)

def downsample(filename):
    data = info_from_file(filename)
    args = data.copy()
    outfilename = filename_from_info(data).splitext()[0] + '.mp3'
    outfilename = down_dir / outfilename
    args['outfilename'] = outfilename
    if not outfilename.parent.exists():
        outfilename.parent.makedirs()
    if outfilename.exists():
        print "%s already exists" % outfilename
        return
    if data['encoding'] == 'ogg':
        infilename = '/tmp/converting.wav'
        command = (
            "oggdec -o %s %s"
            % (shquote(infilename), shquote(filename)))
        result = os.system(command)
        if result:
            print "Error %s" % result
            print "Command:", command
    elif data['encoding'] == 'mp3':
        infilename = filename
        print "Already encoded; hard linking"
        os.link(infilename, outfilename)
        return
    args['infilename'] = infilename
    for key in args:
        args[key] = shquote(unicode(args[key]).encode('UTF-8'))
    command = ("lame --silent --preset cbr 64 -h --tt %(title)s --ta %(artist)s --tl %(album)s --tn %(track)s --add-id3v2 %(infilename)s %(outfilename)s"
               % args)
    print "Encoding to %s" % outfilename
    result = os.system(command)
    if result:
        print "Error %s" % result
        print "Command: %s" % command

def shquote(v):
    return "'%s'" % (v.replace("'", "'\"'\"'"))

def recur_apply(dir, func, *kw):
    BadFile = None
    if not dir.isdir():
        if not dir.ext.lower() in ('.mp3', '.ogg'):
            return
        try:
            func(dir, **kw)
        except BadFile, e:
            print "%s: %s" % (dir, e)
        except:
            print "Bad file: %s" % dir
            raise
    else:
        for ext in ['.mp3', '.ogg']:
            if not dir.exists():
                continue
            for filename in dir.walkfiles('*%s' % ext):
                try:
                    func(filename, **kw)
                except BadFile, e:
                    print "%s: %s" % (filename, e)
                except:
                    print "Bad file: %s" % filename
                    raise

def clean(name):
    if isinstance(name, unicode):
        for val, repl in {u'\xc3\xad': 'i',
                          u'\xc3\xb6': 'o',
                          u'\xc3\xb3': 'a',
                          u'\xc3\xa9': 'e',
                          u'\xc3\xba': 'u',
                          u'\xc3\xb1': 'n',
                          u'\u042c': 'U',
                          u'\u0431': 'b',
                          u'\xc3\xa3': '',
                          u'\xc2\xa1': '',
                          u'\xc3\xa1': 'a',
                          u'\xc3\xa7': 'ca',
                          u'\xc3\x8d': 'i',
                          u'\xc3\xb0': 'd',
                          u'\xc3\x9e': 'p',
                          u'\xc3\x86': 'ae',
                          u'\xc3\x81': 'a',
                          u'\xc3\x93': 'O',
                          u'\xc3\xa8': '',
                          u'\xe2\x80\xa6': '...',
                          u'\xc3\xaa': '',
                          u'\xc3\xa0': 'e',
                          u'\xc2\xb0': 'e',
                          u'\xc2\xbf': '',
                          u'\xc3\xbc': 'u',
                          u'\xc3\x89': '',
                          u'\u044f': '',
                          u'\u0443': '',
                          '`': "'",
                          '_': ' ',
                          }.items():
            name = name.replace(val, repl)
    try:
        name = str(name)
    except:
        print "Bad name:", repr(name), '=', str(name)
        raise
    for val, repl in [(':', ','),
                      ('&amp;', '&'),
                      ('&amp', '&'),
                      ]:
        name = name.replace(val, repl)
    name = re.sub(r'\s+-\s+', '-', name)
    name = re.sub(r'[^a-zA-Z0-9_\- \.&!,\'?()]', '', name)
    name = name.strip()
    return name

def find_track(filename):
    match = re.search(r'[0-9]+', filename.namebase)
    if match is None:
        return None
    return int(match.group(0))

def _prdict(d):
    d = d.items()
    d.sort()
    return d

def main():
    global DISPLAY, TESTING
    global out_dir, down_dir
    options, args = parser.parse_args()
    TESTING = options.simulate
    DISPLAY = options.verbosity or TESTING
    out_dir = path(options.out_dir)
    down_dir = path(options.down_dir)
    filenames = []
    for arg in args:
        if arg.startswith('@'):
            f = open(arg[1:])
            filenames.extend([s.strip() for s in f.readlines()])
            f.close()
        else:
            filenames.append(arg)
    kw = {}
    if options.update:
        assert not options.move and not options.downsample
        func = update_from_filename
    elif options.move:
        assert not options.downsample
        func = update_from_metadata
        kw['copy'] = options.copy
    elif options.downsample:
        func = downsample
    else:
        print 'You must give -m, -u, or -d'
        sys.exit()
    for filename in filenames:
        if not os.path.exists(filename):
            print 'File does not exist: %s' % filename
            continue
        recur_apply(path(filename), func)

if __name__ == '__main__':
    main()
