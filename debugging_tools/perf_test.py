#!/usr/bin/env python
from sys import argv, exit
from time import process_time
from PIL import Image
import image_blender


def _run_test(func_name, pass_count, image_data_1, image_data_2):
    blend_func = getattr(image_blender, func_name)
    start_time = process_time()

    for _ in range(pass_count):
        blend_func(image_data_1, image_data_2)

    return process_time() - start_time

def main():
    IMAGES_DIR = 'images/'
    FUNC_NAMES = (
        'dissolve',

        'darken', 'multiply', 'color_burn', 'linear_burn', 'darker_color',

        'lighten', 'screen', 'color_dodge', 'linear_dodge', 'lighter_color',

        'overlay', 'soft_light', 'hard_light', 'vivid_light', 'linear_light',
        'pin_light', 'hard_mix',

        'difference', 'exclusion', 'subtract', 'divide',

        'hue', 'saturation', 'color', 'luminosity'
    )

    background_bytes = Image.open(IMAGES_DIR + 'background.png').tobytes()
    active_bytes = Image.open(IMAGES_DIR + 'active.png').tobytes()

    if len(argv) < 3:
        pass_count = 1000
    else:
        pass_count = int(argv[2])

    if argv[1] == 'all':
        time_elapsed_total = 0
        print('Running all blend modes %d times...' % pass_count)

        for func_name in FUNC_NAMES:
            mode_name = func_name.replace('_', ' ').title() + ' mode:'
            print('    %-21s' % mode_name, end='', flush=True)

            time_elapsed = _run_test(
                func_name, pass_count, background_bytes, active_bytes
            )

            time_elapsed_total += time_elapsed
            print('%f seconds.' % time_elapsed)

        print('Done in %f seconds.' % time_elapsed_total)
    else:
        func_name = argv[1]
        if func_name not in FUNC_NAMES:
            exit('ERROR: Invalid blend function "%s"' % func_name)

        mode_name = func_name.replace('_', ' ').title()
        print('Running %s mode %d times...' % (mode_name, pass_count))

        time_elapsed = _run_test(
            func_name, pass_count, background_bytes, active_bytes
        )

        print('Done in %f seconds.' % time_elapsed)


if __name__ == '__main__':
    if len(argv) < 2 or argv[1] in ('-h', '--help'):
        print('Performance Test tool ─ Measures the time elapsed on running'
              ' certain (or all) blend function certain amount of times.\n\n'
              'Usage: perf_test.py <func_name|all> [<pass_count=1000>]')
        exit()

    main()
