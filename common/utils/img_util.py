from PIL.Image import Image


def is_image_uniform(img: Image):
    gray_img = img.convert('L')
    min_value, max_value = gray_img.getextrema()
    return min_value == max_value
