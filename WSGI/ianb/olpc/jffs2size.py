import os
import subprocess
import zipfile
from cStringIO import StringIO

COMP_OVERHEAD = 68
ZLIB_CHUNK = 4096
GENERAL_OVERHEAD = 86
DIR_OVERHEAD = GENERAL_OVERHEAD

def file_size(filename):
    size = 0
    f = open(filename, 'rb')
    while 1:
        c = f.read(ZLIB_CHUNK)
        if not c:
            f.close()
            return size + GENERAL_OVERHEAD + len(filename)
        comp_size = len(c.encode('zlib')) + COMP_OVERHEAD
        size += min(comp_size, len(c))
        
def dir_size(dir):
    size = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            size += file_size(os.path.join(dirpath, filename))
        size += DIR_OVERHEAD
    return size

def raw_dir_size(dir):
    size = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            size += os.path.getsize(os.path.join(dirpath, filename))
    return size

def k_size(size):
    return '%iK' % (size / 1000)

def mkfs_size(dir):
    proc = subprocess.Popen(['mkfs.jffs2', '--root', dir], stdout=subprocess.PIPE)
    output, stderr = proc.communicate()
    return len(output)

def zip_size(dir):
    out = StringIO()
    z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            z.write(os.path.join(dirpath, filename))
    z.close()
    return len(out.getvalue())

def tar_size(dir, algo='z'):
    assert algo in ('z', 'j')
    proc = subprocess.Popen(['tar', 'c'+algo, '.'], stdout=subprocess.PIPE, cwd=dir)
    output, stderr = proc.communicate()
    return len(output)

def number_files(dir):
    dirs = 0
    files = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        dirs += len(dirnames)
        files += len(filenames)
    return dirs, files

def print_extensions(dir):
    counts = {}
    total = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            counts[ext] = counts.get(ext, 0)+1
            total += 1
    for ext in counts.keys():
        # Must be more than 0.5% of files:
        if counts[ext] < total/200:
            del counts[ext]
    counts = counts.items()
    # Common extensions first:
    counts.sort(key=lambda x: -x[1])
    width = int(os.environ.get('COLUMNS', 70)) - 13
    max_count = counts[0][1]
    for ext, count in counts[:10]:
        count_width = width*count / max_count
        pad = ' '*(6-len(ext))
        print '%s%s%4i/%2i%%:%s' % (ext or 'none', pad, count, 100*count/total, '*'*(count_width or 1))
    if counts[10:]:
        print 'other extensions:',
        for ext, count in counts[10:]:
            print ('%s:%i' % (ext, count)),

def print_sizes(dir):
    sizes = []
    max_size = 0
    for dirpath, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            sizes.append(os.path.getsize(os.path.join(dirpath, filename)))
    width = int(os.environ.get('COLUMNS', 70))
    max_size = max(sizes)
    ave_size = sum(sizes) / len(sizes)
    print 'Sizes: average %s, range %sb-%s' % (
        k_size(ave_size), min(sizes), k_size(max_size))
    resolution = max_size / width
    size_chunks = {}
    max_count = 0
    for size in sizes:
        size = int(round(size / float(resolution)) * resolution)
        size_chunks[size] = size_chunks.get(size, 0) + 1
        max_count = max(size_chunks[size], max_count)
    size_chunks = size_chunks.items()
    size_chunks.sort()
    total_height = 8
    for height in range(total_height):
        line = []
        for size, count in size_chunks:
            if (count * total_height / max_count) >= total_height - height:
                line.append('+')
            else:
                line.append(' ')
        print ''.join(line)
    print '-'*width
    padding = width - 1 - len(k_size(max_size)) - len(k_size(max_size/2))
    print '0%s%s%s%s' % (' '*(padding/2), k_size(max_size/2), ' '*(padding/2), k_size(max_size))

if __name__ == '__main__':
    import sys
    if not sys.argv[1:]:
        print 'usage: %s DIR1 [DIR2...]' % os.path.basename(sys.argv[0])
        print 'Displays bytes used on a JFFS2 system by the directories (estimated)'
        sys.exit(2)
    for arg in sys.argv[1:]:
        dirs, files = number_files(arg)
        print '%s (%i dirs, %i files)' % (arg, dirs, files)
        print_extensions(arg)
        print_sizes(arg)
        raw_size = raw_dir_size(arg)
        print '  no compression : %s, %s' % (raw_size, k_size(raw_size))
        comp_size = dir_size(arg)
        print '  estimated jffs2: %s, %s (%i%%)' % (comp_size, k_size(comp_size), 100*comp_size/raw_size)
        try:
            mkfs_size = mkfs_size(arg)
        except OSError, e:
            if e.errno != 2:
                raise
            print '  mkfs.jffs2 not installed?'
        else:
            print '  mkfs.jffs2     : %s, %s (%i%%)' % (mkfs_size, k_size(mkfs_size), 100*mkfs_size/raw_size)
        zipped_size = zip_size(arg)
        print '  zipped         : %s, %s (%i%%)' % (zipped_size, k_size(zipped_size), 100*zipped_size/raw_size)
        tgz_size = tar_size(arg)
        print '  .tar.gz        : %s, %s (%i%%)' % (tgz_size, k_size(tgz_size), 100*tgz_size/raw_size)
        tbz2_size = tar_size(arg, 'j')
        print '  .tar.bz2       : %s, %s (%i%%)' % (tbz2_size, k_size(tbz2_size), 100*tbz2_size/raw_size)
        
