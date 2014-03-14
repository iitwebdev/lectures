import sys
import os
from cmdutils import OptionParser, CommandError, main_func
from explodeimage.explode import explode_image

## The long description of how this command works:
description = """\
"""

parser = OptionParser(
    usage="%prog [OPTIONS] ARGS",
    version_package='ExplodeImage',
    description=description,
    max_args=1,
    min_args=1,
    ## Set this to true to create a logger:
    #use_logging=False,
    )

parser.add_option(
    '-w', '--width',
    dest='width',
    type="int",
    metavar="PIXELS",
    help="Number of pictures wide to explode image")

parser.add_option(
    '-r', '--ratio',
    dest='ratio',
    type="float",
    metavar="WIDTH/HEIGHT",
    help="The ratio of WIDTH to HEIGHT, default 6/4==1.5",
    default=1.5)

parser.add_option(
    '--side', '--trim-sides',
    dest='trim_sides',
    action='store_true',
    help='Trim the sides to fit photos (otherwise trim top/bottom)')

parser.add_option(
    '-o', '--output',
    dest='output_dir',
    metavar='DIR',
    default='./exploded-images',
    help='Directory to put images')


parser.add_verbose()

@main_func(parser)
def main(options, args):
    filename = args[0]
    if not os.path.exists(filename):
        raise CommandError(
            "File %s does not exist" % filename)
    if not options.width:
        raise CommandError(
            "You must provide a --width argument")
    output_dir = options.output_dir
    if not os.path.exists(output_dir):
        options.logger.notify('Creating directory %s' % output_dir)
        os.makedirs(output_dir)
    else:
        options.logger.debug('Directory %s exists' % output_dir)
    explode_image(
        filename,
        output_dir,
        options.width,
        options.ratio,
        options.trim_sides,
        options.logger)

if __name__ == '__main__':
    main()
