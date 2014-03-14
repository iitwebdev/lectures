try:
    from PIL import Image
except ImportError:
    import Image

def explode_image(
    image_filename,
    output_dir,
    width_count,
    ratio,
    trim_sides,
    logger):
    image = Image.open(image_filename)
    width, height = image.size
    logger.notify('%s: %sx%s' % (
        image_filename, width, height))
    seg_width = width / width_count
    seg_height = int(seg_width / ratio)
    height_count = height / seg_height
    logger.notify('Creating %sx%s images' % (width_count, height_count))
    logger.notify('Each image is %sx%s' % (seg_width, seg_height))
    
