import io
from PIL import Image, ImageFile, UnidentifiedImageError

ImageFile.LOAD_TRUNCATED_IMAGES = True


def resize_image_to_binary(input_image, max_width=1000):
    try:
        original_image = Image.open(input_image)
    except (UnidentifiedImageError, OSError, IOError):
        return
    width, height = original_image.size
    if width > max_width:
        height = height * max_width // width
        width = max_width
    resized_image = original_image.resize((width, height))
    io_binary = io.BytesIO()
    resized_image.save(fp=io_binary, format=original_image.format)
    result = io_binary.getvalue()
    io_binary.close()
    return result
