#!/usr/bin/perl -w
# Copyright © 2005 Jamie Zawinski <jwz@jwz.org>
#
# Permission to use, copy, modify, distribute, and sell this software and its
# documentation for any purpose is hereby granted without fee, provided that
# the above copyright notice appear in all copies and that both that
# copyright notice and this permission notice appear in supporting
# documentation.  No representations are made about the suitability of this
# software for any purpose.  It is provided "as is" without express or 
# implied warranty.

###############################################################################
#
#     picturetile.pl
#
#     Takes a bunch of images and tiles them into one large image.
#     Not so much a collage, as a "photo wall."
#
#     The images are selected randomly from the given directory, and packed
#     together as tightly as possible.  Images that are very small are
#     assumed to be thumbnails and are ignored.  No image will be used more
#     than once, and the images need not be of the same size or aspect ratio.
#
#     Created: 14-Mar-2005.
#
###############################################################################
#
# Options:
#
#     --verbose        Loudness.  -vvv for more.
#     --size WxH       Max size of the resultant image.
#     --margin N       Spacing between images.  default 8 pixels.
#                      This may be negative to make the images overlap.
#     --border N       Size of the overall outside border.  Default 8 pixels.
#     --directory DIR  Directory tree where images are found.
#     --background C   Background color, default white.
#     --scale N        Resize the sub-images before pasting; default 1.0.
#     --uniform        If all your images are the same size, use this to get
#                      a more regular grid (i.e., all lines flush-left.)
#     --checkpoint     Write the output file at the end of each line, as well
#                      as at the very end (so you can watch the progress.)
#
###############################################################################
#
# Example:
#
#      Suppose you have a bunch of images from a 6 megapixel camera, and you
#      want to end up with a file that you can have printed on a 30" x 60"
#      sheet at 200 DPI, where each individual photo is snapshot-sized
#      (meaning around 5" in its longest dimension.)
#
#      The size of the output file should be 30" x 200 DPI by 60" x 200 DPI,
#      or 6000 x 12000 pixels.
#
#      Within that image, each individual photo should be 5" x 200 DPI, or
#      1000 pixels.  Since 6 megapixel images are a mixture of 3072 x 2048
#      landscape and 2048 x 3072 portrait, that means they need to be scaled
#      down by 1000/3072, or 0.3255.
#
#      If you want a half-inch border on the outside, that's .5" x 200 DPI
#      or 100 pixels.
#
#      So you'd invoke this program as:
#
#          picturetile.pl --size 6000x12000           \
#                         --scale 0.3255              \
#                         --border 100                \
#                         --directory /the/pictures/  \
#                         output.jpg
#
#      That will make use of around 80 images from that directory, and will
#      take about five minutes on a 2GHz machine.  It will also use a truly
#      gargantuan amount of RAM, and result in an output file of 4-5 MB.
#
#      You can write a TIFF (or just about anything else) instead of a JPEG
#      by using the appropriate output file extension.
#
###############################################################################
#
# Details:
#
#     The images are packed in pretty tightly, but bin packing is NP-complete,
#     so the packing will not be optimal.  This program usually gets at least
#     75% coverage, which isn't so bad.
#
#     The traditional bin-packing algorithm is to sort the objects by size,
#     and pack them in largest to smallest ("first-fit decreasing"), but that
#     doesn't result in an aesthetically pleasing result (all the big images
#     would be clustered in one corner.)
#
#     The method used here is a Tetris-like strategy:
#
#       - place the first image at the bottom left;
#       - for each subsequent image:
#          - place it just to the right of the previous image, at the top edge;
#          - drop it straight down until it collides with another image;
#          - then move it left, if possible;
#          - then drop again, if possible.
#
#     Then the overall image is cropped to the resultant bounding box, and
#     written out.
#
###############################################################################
#
# Alternatives:
#
#     If all your images are exactly the same size, or if you want them
#     arranged on a regular grid, then the ImageMagick "montage" program
#     will probably serve you better than this script.
#
###############################################################################
#
# Discussion:
#     http://jwz.livejournal.com/455804.html
#
###############################################################################


require 5;
use diagnostics;
use strict;

use POSIX ':fcntl_h';				# S_ISLNK was here in Perl 5.6
import Fcntl ':mode' unless defined &S_ISLNK;	# but it is here in Perl 5.8

use Image::Magick;

use bytes;  # Larry can take Unicode and shove it up his ass sideways.
            # Perl 5.8.0 causes us to start getting incomprehensible
            # errors about UTF-8 all over the place without this.

my $progname = $0; $progname =~ s@.*/@@g;
my $version = q{ $Revision: 1.3 $ }; $version =~ s/^[^0-9]+([0-9.]+).*$/$1/;

my $verbose = 0;

my $image_directory;
my $canvas_width;
my $canvas_height;
my $margin = 8;
my $border = 8;
my $image_scale = 1.0;
my $bg_color = 'white';
my $output_filename;
my $uniform_p = 0;
my $checkpoint_p = 0;

# This matches files that we are allowed to use as images (case-insensitive.)
# Anything not matching this is ignored.  This is so you can use an image
# directory at directory trees that have things other than images in
# them, but it assumes that you gave your images sensible file extensions.
#
my $good_file_re = '\.(gif|p?jpe?g|png|tiff?|xbm|xpm)$';


# Images that are are smaller than this size are rejected: this is so that
# you can use an image directory tree that contains both big images and
# thumbnails, and have it only select the big versions.
#
my $min_image_width  = 255;
my $min_image_height = 255;


my @boxes = ();
my %used_images;
my $canvas;
my $area;
my $cursorx;
my $cursory;
my $out_of_files = 0;

my ($X, $Y, $W, $H) = (0, 1, 2, 3);  # "struct box"

my @all_files = ();     # list of "good" files we've collected
my %seen_inodes;        # for breaking recursive symlink loops
my $skip_count = 0;     # number of files skipped, for diagnostic messages
my $dir_count = 1;      # number of directories seen, for diagnostic messages

# mostly lifted from "xscreensaver-getimage-file"
#
sub find_all_files_1 {
  my ($dir) = @_;

  print STDERR "$progname: reading dir $dir/...\n" if ($verbose > 4);

  local *DIR;
  if (! opendir (DIR, $dir)) {
    print STDERR "$progname: couldn't open $dir: $!\n" if ($verbose > 1);
    return;
  }
  my @files = readdir (DIR);
  closedir (DIR);

  my @dirs = ();

  foreach my $file (@files) {
    next if ($file =~ m/^\./);      # ignore dot files/dirs

    $file = "$dir/$file";
    my @st = stat($file);
    my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
        $atime,$mtime,$ctime,$blksize,$blocks) = @st;

    if ($#st == -1) {
      if ($verbose > 1) {
        my $ll = readlink $file;
        if (defined ($ll)) {
          print STDERR "$progname: dangling symlink: $file -> $ll\n";
        } else {
          print STDERR "$progname: unreadable: $file\n";
        }
      }
      next;
    }

    next if ($seen_inodes{"$dev:$ino"}); # break symlink loops
    $seen_inodes{"$dev:$ino"} = 1;

    if (S_ISDIR($mode)) {
      push @dirs, $file;
      $dir_count++;
      print STDERR "$progname:   found dir  $file\n" if ($verbose > 4);
    } elsif (S_ISREG($mode) || S_ISLNK($mode)) {

      if ($file =~ m/[~%\#]$/ ||               # backup file, or
          ! ($file =~ m/$good_file_re/io)) {   # no image extension
        $skip_count++;
        print STDERR "$progname:   skip file $file\n" if ($verbose > 4);
      } else {
        push @all_files, $file;
        print STDERR "$progname:   found file $file\n" if ($verbose > 4);
      }
    } elsif ($verbose > 4) {
      print STDERR "$progname:   nonreg $file\n";
    }
  }

  foreach (@dirs) {
    find_all_files_1 ($_);
  }
}


# Permutes the array (reference) in place.  "Fisher Yates Shuffle".
#
sub shuffle_array {
  my ($array) = @_;
  for (my $i = @$array; --$i;) {
    my $j = int rand ($i+1);
    next if ($i == $j);
    @$array[$i,$j] = @$array[$j,$i];
  }
}


sub find_all_files {
  my ($dir) = @_;

  $dir =~ s@/+$@@g;

  print STDERR "$progname: recursively reading $dir...\n" if ($verbose > 1);
  find_all_files_1 ($dir);
  print STDERR "$progname: found " . ($#all_files+1) .
               " file" . ($#all_files == 0 ? "" : "s") .
               " in $dir_count dir" . ($dir_count == 1 ? "" : "s") .
               "; skipped $skip_count file" . ($skip_count == 1 ? "" : "s") .
               ".\n"
    if ($verbose > 1);

  if ($#all_files < 0) {
    print STDERR "$progname: no files in $dir\n";
    exit 1;
  }

  shuffle_array (\@all_files);
}


# Returns the name of a random unused image from the preloaded list.
# undef when no more.
#
sub random_image_name {

  my $max_tries = $#all_files+1;

  for (my $i = 0; $i < $max_tries; $i++) {
    my $file = shift @all_files;  # take it off the front
    push @all_files, $file;       # put it on the back
    return $file if (!defined ($used_images{$file}));
  }

  print STDERR "$progname: out of files ($max_tries) in $image_directory\n";
  $out_of_files = 1;
  return undef;
}


sub max { return ($_[0] > $_[1] ? $_[0] : $_[1]); }
sub min { return ($_[0] < $_[1] ? $_[0] : $_[1]); }

# Whether the two rectangles intersect.
# Args are references to 4 element arrays of [ X Y W H ]
#
sub boxes_overlap_p {
  my ($a, $b) = @_;

  my $maxtop   = max($a->[$Y], $b->[$Y]);
  my $minbot   = min($a->[$Y] + $a->[$H] - 1, $b->[$Y] + $b->[$H]);
  return 0 if ($maxtop >= $minbot);

  my $maxleft  = max($a->[$X], $b->[$X]);
  my $minright = min($a->[$X] + $a->[$W] - 1, $b->[$X] + $b->[$W]);
  return ($maxleft < $minright);
}


# Returns (one of) the box(es) with which we collided, or undef.
#
sub box_collides_p {
  my ($a) = @_;

  my $canvas_height1 = ($canvas_height + ($margin < 0 ? $margin : 0)
                        - $border);

  # collide with wall
  return $a if (#$a->[$X] < 0 ||
               #$a->[$Y] < 0 ||
               #$a->[$X] + $a->[$W] >= $canvas_width1 ||
                $a->[$Y] + $a->[$H] >= $canvas_height1);

  # collide with another box.
  # iterate backwards to compare with recently-added first.
  for (my $i = $#boxes; $i >= 0; $i--) {
    my $b = $boxes[$i];
    return $b if (boxes_overlap_p ($a, $b));
  }

  return undef;
}


# Place a new image in the canvas.  Returns 0 if ok, 1 if failed.
#
# When last_resort_p is true, uses an alternate algorithm intended to
# better fill in any remaining gaps in the top row.
#
sub place_image {
  my ($last_resort_p) = @_;

  return 1 if ($out_of_files);

  my $max_retries = 20;
  my $retries = 0;

  my $img = undef;
  my $status;

  my $eol_count = 0;

  my @aa;
  my $a = \@aa;
  my $b = undef;
  my $name;
  my $name2;

  my $margin0 = max ($margin, 0);
  my $canvas_width1  = ($canvas_width  + ($margin < 0 ? $margin : 0)
                        - $border);
  my $canvas_height1 = ($canvas_height + ($margin < 0 ? $margin : 0)
                        - $border);

  while ($last_resort_p || $retries++ < $max_retries) {

    if (!$name || ($retries > 0 && !$last_resort_p)) {
      $name = random_image_name();
      return 0 if (!defined ($name));  # out of files!
      $name2 = $name;
      $name2 =~ s@^.*/@@;
    }

    undef $img;
    $img = Image::Magick->new;
    $status = $img->Read ($name);
    imagemagick_check_error ($status);

    ($a->[$W], $a->[$H]) = $img->Get ('width', 'height');
    if (!$a->[$W] || !$a->[$H]) {
      # bad image
      $used_images{$name} = 1;  # don't try it again
      undef $img;
      next;
    }

    if ($a->[$W] < $min_image_width || $a->[$H] < $min_image_height) {
      print STDERR "$progname: $name2: too small ($a->[$W] x $a->[$H])\n"
        if ($verbose > 2);
      undef $img;
      $used_images{$name} = 1;  # don't try it again
      $retries--;               # "too small" doesn't count as a retry
      undef $name;
      next;
    }

    if ($image_scale != 1.0) {
      my $ow = $a->[$W];
      my $oh = $a->[$H];
      $a->[$W] = int ($a->[$W] * $image_scale + 0.5);
      $a->[$H] = int ($a->[$H] * $image_scale + 0.5);
      #print STDERR "scaling ${ow}x${oh} to $a->[$W]x$a->[$H]  $name2\n"
      #  if ($verbose > 3);
      $status = $img->Scale ('width'  => $a->[$W],
                             'height' => $a->[$H]);
      imagemagick_check_error ($status);
    }

    $a->[$W] += $margin;
    $a->[$H] += $margin;

    $a->[$X] = $cursorx;
    $a->[$Y] = max($border + $margin0, $cursory - $a->[$H] - 1);

    if ($a->[$X] + $a->[$W] >= $canvas_width1) {	# end of line
      $cursorx = $border + $margin0;
      $a->[$X] = $cursorx;
      $eol_count++;

      if ($checkpoint_p && $#boxes > 0) {
        imagemagick_finish ();
      }
    }

    # If this image is the first one on the row, shift it to the right
    # by a random amount, so that both the left and right margins are
    # ragged (instead of everything being flush-left.)
    #
    my $left_edge = $border + $margin0;
    if (!$uniform_p && $a->[$X] <= $border + $margin0) {
      $a->[$X] += int (rand($a->[$W] / 2));
      if ($a->[$X] < $border + $margin0) { $a->[$X] = $border + $margin0; }
      if ($a->[$X] > $canvas_width - $a->[$W]) {
        $a->[$X] = $canvas_width - $a->[$W];
      }
      $left_edge = $a->[$X];
    }


    if (! ($b = box_collides_p ($a))) {

      # Drop the image until it can drop no more
      #
      do {
        $a->[$Y]++;
      } while (! ($b = box_collides_p ($a)));
      $a->[$Y]--;

      # now go left as far as we can (a tetris dance)
      #
      do {
        $a->[$X]--;
      } while ($a->[$X] >= $left_edge &&
               !($b = box_collides_p ($a)));
      $a->[$X]++;

      # and finally try to drop again.
      #
      do {
        $a->[$Y]++;
      } while (! ($b = box_collides_p ($a)));
      $a->[$Y]--;


      # If this image is on the bottom row, shift it up by a random amount,
      # so that both the top and bottom margins are ragged (instead of
      # everything being flush-bottom.)
      #
      if (!$uniform_p && $a->[$Y] + $a->[$H] + 2 >= $canvas_height1) {
        $a->[$Y] -= int (rand($a->[$H] / 2));
        if ($a->[$Y] < $border + $margin0) { $a->[$Y] = $border + $margin0; }
        if ($a->[$Y] > $canvas_height1 - $a->[$H]) {
          $a->[$Y] = $canvas_height1 - $a->[$H];
        }
      }

      if ($a->[$Y] >= $border + $margin0) {

        $used_images{$name} = 1;
        push @boxes, $a;
        $area += ($a->[$W] - $margin) * ($a->[$H] - $margin);
        $cursorx = max ($cursorx, $a->[$X] + $a->[$W]);
        $cursory = min ($cursory, $a->[$Y]);

        if ($verbose) {
          my $x = $a->[$X];
          my $y = $a->[$Y];
          my $w = $a->[$W] - $margin;
          my $h = $a->[$H] - $margin;
          print STDERR sprintf ("%s %3d %2d%% %5dx%-5d \@ %5d,%-5d %s\n",
                                ($last_resort_p ? "IMG" : "img"),
                                $#boxes+1,
                                int (($area * 100) /
                                     ($canvas_width * $canvas_height)),
                                $w, $h, $x, $y, $name2);
        }

        $status = $canvas->Composite ( 'image' => $img,
                                       'x' => $a->[$X],
                                       'y' => $a->[$Y] );
        imagemagick_check_error ($status);
        undef $img;
        return 0;

      } elsif ($verbose > 3) {
        print STDERR "$progname: fail$last_resort_p " .
          "(drop $a->[$X],$a->[$Y]): $name2\n";
      }
    } elsif ($verbose > 3) {
      print STDERR "$progname: fail$last_resort_p " .
        "(top $a->[$X],$a->[$Y]): $name2\n";
    }

    if ($last_resort_p) {

      if ($b) {
        $cursorx = $b->[$X] + $b->[$W];    # right of collision box
      } else {
        $cursorx += ($margin != 0 ? $margin : 1);
      }

      if ($eol_count > 0) {
        print STDERR "$progname: fail$last_resort_p " .
          "(last $a->[$X],$a->[$Y]): $name2\n"
          if ($verbose > 3);
        return 1;
      }
    }
  }

  undef $img;

  return 1;  # done: too many retries
}


# Find the overall bounding box of the canvas, and crop to that.
# Otherwise we end up with larger margins on the right and top edges.
#
sub crop_to_bbox {
  my $status;
  my $minx = 999999999;
  my $miny = 999999999;
  my $maxx = 0;
  my $maxy = 0;

  my $margin0 = max ($margin, 0);

  error ("total layout failure?") unless ($#boxes >= 0);
  foreach my $box (@boxes) {
    $minx = min($minx, $box->[$X]);
    $miny = min($miny, $box->[$Y]);
    $maxx = max($maxx, $box->[$X] + $box->[$W]);
    $maxy = max($maxy, $box->[$Y] + $box->[$H]);
  }

  $minx -= $border + $margin0;
  $miny -= $border + $margin0;
  $minx = 0 if ($minx < 0);
  $miny = 0 if ($miny < 0);

  $maxx += $border;
  $maxy += $border;

  if ($margin < 0) {
    $maxx -= $margin;
    $maxy -= $margin;
  }

  my $ow = $canvas_width;
  my $oh = $canvas_height;
  $canvas_width  = $maxx - $minx;
  $canvas_height = $maxy - $miny;
  my $geom = "${canvas_width}x${canvas_height}+$minx+$miny";
  my $pct = int (($canvas_width * $canvas_height * 100) / ($ow * $oh));
  print STDERR "$progname: cropping ${ow} x ${oh} to " .
               "${canvas_width} x ${canvas_height} \@ $minx,$miny ($pct%)\n"
    if ($verbose);
  $status = $canvas->Crop ( 'geometry' => $geom );
  imagemagick_check_error ($status);
}


# Do the full layout.
#
sub place_images {

  print STDERR "$progname: beginning layout...\n"
    if ($verbose);

  @boxes = ();
  $area = 0;

  my $margin0 = max ($margin, 0);
  my $canvas_height1 = ($canvas_height + ($margin < 0 ? $margin : 0)
                        - $border);

  $cursorx = $border + $margin0;
  $cursory = $canvas_height1 - $margin0;

  1 while (!place_image (0));     # fill left-to-right, bottom-to-top.
  1 while (!place_image (1));     # try to fill the rest of the top row.
  1 while (!place_image (1));     # twice.
  1 while (!place_image (1));     # thrice.
  crop_to_bbox();
}


# Create the output image canvas, and initialize it to the background color.
#
sub imagemagick_init {
  my $status;

  $canvas = Image::Magick->new;

  print STDERR "$progname: creating canvas ${canvas_width}x${canvas_height}\n"
    if ($verbose);
  $status = $canvas->Set (size => "${canvas_width}x${canvas_height}");
  imagemagick_check_error ($status);

  print STDERR "$progname: background color $bg_color\n"
    if ($verbose);
  $status = $canvas->ReadImage ("xc:$bg_color");
  imagemagick_check_error ($status);
}


# Write the canvas to the output file.  This can be called multiple times.
#
sub imagemagick_finish {

  my $status;
  my ($w, $h) = $canvas->Get ('width', 'height');

  $status = $canvas->Write ( 'filename' => $output_filename );
  imagemagick_check_error ($status);

  my ($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size,
      $atime,$mtime,$ctime,$blksize,$blocks) = stat($output_filename);
  my $k = int (($size + 1023) / 1024);
  if ($k < 1024) {
    $k = "${k}K";
  } else {
    $k = sprintf ("%.1fM", $k / 1024.0);
  }

  my $pct = int (($area * 100) / ($canvas_width * $canvas_height));
  my $n = $#boxes + 1;
  print STDERR "$progname: wrote $n images to $output_filename " .
    "(${k}; ${w} x $h; $pct%)\n";
}


# Check and print error status from various Image::Magick commands,
# and die if it's not just a warning.
#
sub imagemagick_check_error {
  my ($err) = @_;
  return unless $err;
  print STDERR "$progname: $err\n";
  $err =~ /(\d+)/;
  exit (1) if ($err >= 400);
}


sub error {
  my ($err) = @_;
  print STDERR "$progname: $err\n";
  exit 1;
}

sub usage {
  print STDERR "usage: $progname " .
    "[--verbose] --size WxH --margin pixels --border pixels\n" .
    "\t\t      --directory image-dir --background color\n" .
    "\t\t      --scale float [--checkpoint] output-file\n\n";
  exit 1;
}

sub main {

  my $size;

  while ($#ARGV >= 0) {
    $_ = shift @ARGV;
    if ($_ eq "--verbose") { $verbose++; }
    elsif (m/^-v+$/) { $verbose += length($_)-1; }
    elsif (m/--?dir(ectory)?/) { $image_directory = shift @ARGV; }
    elsif (m/--?size/)   { $size = shift @ARGV; }
    elsif (m/--?margin/) { $margin = int(shift @ARGV); }
    elsif (m/--?border/) { $border = int(shift @ARGV); }
    elsif (m/--?scale/)  { $image_scale = 0.0 + shift @ARGV; }
    elsif (m/--?(bg|background)/) { $bg_color = shift @ARGV; }
    elsif (m/--?check(point)?/) { $checkpoint_p++; }
    elsif (m/--?uni(form)?/) { $uniform_p++; }
    elsif (m/^-./) { print STDERR "$progname: unknown option $_\n";
                     usage; }
    elsif (!defined($output_filename)) { $output_filename = $_; }
    else { usage; }
  }

  error ("no output filename specified") unless ($output_filename);
  error ("no image directory specified") unless ($image_directory);
  error ("no size specified") unless ($size);
  error ("border cannot be negative (did you mean --margin?)")
    unless ($border >= 0);
  error ("unparsable size: $size")
    unless ($size =~ m/^(\d+)\s*x\s*(\d+)$/);
  ($canvas_width, $canvas_height) = ($1, $2);
  error ("bad scale: $image_scale") if ($image_scale <= 0);

  find_all_files ($image_directory);
  imagemagick_init ();
  place_images ();
  imagemagick_finish ();
}

main;
exit 0;
