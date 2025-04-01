from PIL.Image import Image

from common.io.file_sys import fs

def save_bytes_as_image(image_bytes: bytes, format="png") -> str:
    """
    Save bytes data as an image to temp file.
    :param image_bytes: Bytes data
    :param format: png/jpg...
    :return:
    """
    img_path = fs.create_temp_file_descriptor(prefix="imgcap", suffix=f".{format}", type="image")

    with open(img_path, "wb") as image_file:
        image_file.write(image_bytes)
        return img_path


def is_image_uniform(img: Image):
    gray_img = img.convert('L')
    min_value, max_value = gray_img.getextrema()
    return min_value == max_value
