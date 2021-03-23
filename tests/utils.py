import os.path as path
from PIL import Image


DATA_PATH = path.join(path.abspath(path.dirname(__file__)), 'images')

def full_name(folder, filename):
    return path.join(DATA_PATH, folder, filename)


if hasattr(Image, 'frombytes'):
    frombytes = Image.frombytes     # latest Pillow
else:
    frombytes = Image.fromstring    # PIL and older Pillow versions


def tobytes(image):
    if hasattr(image, 'tobytes'):
        return image.tobytes()      # latest Pillow
    return image.tostring()         # PIL and older Pillow versions
