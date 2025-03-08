from common.utils.file_util import create_temp_file


def save_bytes_as_image(image_bytes: bytes, format="png") -> str:
    """
    Save bytes data as an image to temp file.
    :param image_bytes: Bytes data
    :param format: png/jpg...
    :return:
    """
    img_path = create_temp_file(prefix="imgcap", suffix=f".{format}", tmpdir="image")

    with open(img_path, "wb") as image_file:
        image_file.write(image_bytes)
        return img_path
