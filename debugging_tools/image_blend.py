#!/usr/bin/env python
from sys import argv, exit
from PIL import Image
import image_blender


def main():
    IMAGES_DIR = 'images/'

    background = Image.open(IMAGES_DIR + 'background.png')
    background_bytes = background.tobytes()
    active_bytes = Image.open(IMAGES_DIR + 'active.png').tobytes()
    size = background.size

    mode_name = argv[1].replace('_', ' ').title()
    print('Blending using %s mode...' % mode_name)

    blend_func = getattr(image_blender, argv[1])
    result_bytes = blend_func(background_bytes, active_bytes)
    result = Image.frombytes('RGBA', size, result_bytes)

    if len(argv) < 3:
        file_name = 'result.png'
    else:
        file_name = argv[2] + '.png'
    result.save(IMAGES_DIR + file_name)
    print('Saved as "%s".' % file_name)


if __name__ == '__main__':
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print('Image Blend tool ─ Blends two images together using specified'
              ' blend function.\n\n'
              'Usage: image_blend.py <func_name> [<save_as=result>]\n'
              '       NOTE: All file names are relative to "images" dir!')
        exit()

    main()
