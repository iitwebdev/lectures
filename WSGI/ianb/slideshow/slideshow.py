#!/usr/bin/env python

try:
    import Image
except ImportError:
    print 'You must install PIL:'
    print '  http://www.pythonware.com/library/pil/handbook/index.htm'
    print
    raise
try:
    import optparse
except ImportError:
    try:
        import optik as optparse
    except ImportError:
        print 'You must install optik: (or use Python 2.3)'
        print '  http://optik.sourceforge.net/'
        print
        raise
import os
import cgi
try:
    import EXIF
except ImportError:
    # Then EXIF is not installed; cannot read EXIF comments:
    #    http://home.cfl.rr.com/genecash/digital_camera/EXIF.py
    EXIF = None
import gzip

thumbnailPatterns = [
    '%(base)s-tn.jpg',
    '%(base)s-thumb.jpg',
    '%(base)s.thumb.jpg',
    '%(base)s-tn%(ext)s',
    '%(base)s.thumb%(ext)s',
    '%(base)s-thumb%(ext)s',
    ]

mediumPatterns = [
    '%(base)s-medium.jpg',
    '%(base)s-medium%(ext)s',
    ]

imageExtensions = [
    '.jpg',
    '.jpeg',
    '.gif',
    '.png',
    '.bmp',
    ]

def check_size(options, opt, value):
    if 'x' not in value:
        raise optparse.OptionValueError(
            'option %s: value %r must be in the format WIDTHxHEIGHT'
            % (opt, value))
    width, height = value.split('x', 1)
    try:
        height = int(height)
        width = int(width)
    except ValueError:
        raise optparse.OptionValueError(
            'option %s: width and height must be integers (%r)'
            % (opt, value))
    return (width, height)

optparse.Option.TYPES += ('size',)
optparse.Option.TYPE_CHECKER['size'] = check_size

parser = optparse.OptionParser()
parser.add_option('-s', '--size',
                  dest='size',
                  help='Maximum image size',
                  metavar='WIDTHxHEIGHT',
                  type='size',
                  default=(650, 500))
parser.add_option('-t', '--thumbsize',
                  dest='thumbSize',
                  help='Maximum thumbnail size',
                  metavar='WIDTHxHEIGHT',
                  type='size',
                  default=(300, 175))
parser.add_option('-u', '--url',
                  dest='baseURL',
                  help='Base URL',
                  metavar='URL')
parser.add_option('--slideshow',
                  dest='slideshowURL',
                  help='URL of slideshow.js',
                  metavar='URL',
                  default='./')
parser.add_option('--no-thumb',
                  dest='thumbnail',
                  action='store_false',
                  default=True,
                  help="Do not show thumbnails in slideshow")

def main(options, args):
    if not args:
        args = ['.']
    for arg in args:
        processDir(arg, options)

def processDir(dir, options):
    allFiles = []
    for filename in os.listdir(dir):
        filename = os.path.join(dir, filename)
        if os.path.splitext(filename)[1].lower() not in imageExtensions:
            continue
        # Don't make thumbnails of thumbnails and so on:
        if checkPattern(filename, thumbnailPatterns +
                        mediumPatterns):
            continue
        allFiles.append(processFile(filename, options))
    createIndex(dir, options, allFiles)

def processFile(filename, options):
    base, ext = os.path.splitext(filename)
    im = Image.open(filename)
    attrs = {'filename': os.path.abspath(filename)}
    if im.size[0] > options.size[0] or im.size[1] > options.size[1]:
        attrs['href'] = createThumb(filename, options.size,
                                    '%s-medium.jpg',
                                    mediumPatterns)
        attrs['fullsrc'] = filename
    else:
        attrs['href'] = filename
    attrs['thumbsrc'] = createThumb(filename, options.thumbSize,
                                    '%s-thumb.jpg',
                                    thumbnailPatterns)
    return attrs

def createThumb(filename, size, filenameTemplate, patterns):
    existing = checkExists(filename, patterns)
    if existing:
        return existing
    thumb = filenameTemplate % os.path.splitext(filename)[0]
    im = Image.open(filename)
    im.thumbnail(size)
    im.save(thumb)
    return thumb

def checkExists(filename, patterns):
    data = {
        'base': os.path.splitext(filename)[0],
        'ext': os.path.splitext(filename)[1],
        'filename': filename}
    for pattern in patterns:
        if os.path.exists(pattern % data):
            return pattern % data
    return None

def checkPattern(filename, patterns):
    data = {
        'base': '',
        'ext': os.path.splitext(filename)[1],
        'filename': '',
        }
    for pattern in patterns:
        if filename.endswith(pattern % data):
            return True
    return False

def createIndex(dir, options, allFiles):
    filename = os.path.join(dir, 'index.html')
    f = open(filename, 'w')
    f.write('<html><head><title>Slideshow</title>\n')
    slideshowURL = options.slideshowURL
    if not slideshowURL.endswith('slideshow.js'):
        if not slideshowURL.endswith('/'):
            slideshowURL += '/';
        slideshowURL += 'slideshow.js';
    f.write('<script type="text/javascript" src="%s"></script>\n'
            % slideshowURL)
    f.write('</head>\n')
    f.write('<body>\n')
    f.write('<div id="images">\n');
    for attrs in allFiles:
        imageFilename = attrs['filename']
        del attrs['filename']
        f.write('<a %s>%s</a><br>\n'
                % (' '.join(['%s="%s"' % (n, cgi.escape(v, 1))
                             for n, v in attrs.items()]),
                   findComments(imageFilename)))
    f.write('</div>\n')
    f.write('<script type="text/javascript>\n')
    slideshowOptions = {'fillStyles': 'true',
                        'imageHeight': "'%spx'" % options.size[1]}
    if not options.thumbnail:
        slideshowOptions['useThumbnails'] = "false"
    f.write("""\
    Slideshow('images', {%s});
    """ % (',\n'.join(['%s: %s' % (k, v) for k, v
                       in slideshowOptions.items()])))
    f.write('</script>\n')
    f.write('</body></html>\n')
    f.close()

def findComments(filename):
    if os.environ.has_key('HOME'):
        gthumbPath = os.path.join(os.environ['HOME'], '.gnome2', 'gthumb',
                                  'comments',
                                  os.path.abspath(filename)[1:]) + '.xml'
        if os.path.exists(gthumbPath):
            f = gzip.open(gthumbPath)
            content = f.read()
            f.close()
            content = content[content.find('<Note>')+6:content.find('</Note>')]
            content.replace('\n', '<br>\n')
            return content
    if EXIF:
        data = EXIF.process_file(open(filename, 'rb'))
        if data.has_key('EXIF UserComment'):
            comment = data['EXIF UserComment'].printable
            comment = comment.strip('\0').strip()
            if comment:
                return comment
    return os.path.basename(os.path.splitext(filename)[0])

if __name__ == '__main__':
    options, args = parser.parse_args()
    main(options, args)
    
