#!/usr/bin/env python
from sys import argv, exit
from PIL import Image, ImageMath


IMAGES_DIR = 'images/'


def make_deviation_map(ch1, ch2):
    return ImageMath.eval('127 + ch2 - ch1', ch1=ch1, ch2=ch2).convert('L')

def make_luminance_map(bands):
    return ImageMath.eval(
        '(30*r + 59*g + 11*b + 50) / 100',
        r=bands[0], g=bands[1], b=bands[2]
    ).convert('L')

def get_color_stats(ch):
    return sorted((c, n) for n, c in ch.getcolors())

def highlight_deviations(im):
    return im.point(lambda c: c if c == 127 else 127 + (c - 127)*10)


def stats_repr_gen(stats):
    for c, n in stats:
        yield '%3d: %5d' % (c, n)

def main():
    im1 = Image.open(IMAGES_DIR + argv[1]).split()
    im2 = Image.open(IMAGES_DIR + argv[2]).split()

    count = min(len(im1), len(im2))

    ch_dev_maps = [x for x in map(make_deviation_map, im1[:count], im2[:count])]
    lum_dev_map = make_deviation_map(
        make_luminance_map(im1), make_luminance_map(im2)
    )

    if len(argv) >= 4:
        base_name = IMAGES_DIR + argv[3]

        highlight_deviations(
            Image.merge('RGB', ch_dev_maps[:3])
        ).save(base_name + '.png')
        if count == 4:
            highlight_deviations(ch_dev_maps[3]).save(base_name + '.alpha.png')

        highlight_deviations(lum_dev_map).save(base_name + '.lum.png')

    channels = ('red  ', 'grn  ', 'blu  ', 'alp  ')
    ch_dev_stats = (x for x in map(get_color_stats, ch_dev_maps))
    lum_dev_stats = get_color_stats(lum_dev_map)

    print('Deviation stats:\n'
          '    dev = 127 ─ no deviation\n'
          '    dev < 127 ─ negative deviation\n'
          '    dev > 127 ─ positive deviation\n\n'
          'chnl  dev: count  ...\n'
          '════════════════════════════════════════')
    for ch, stats in zip(channels, ch_dev_stats):
        ch_stats_repr = stats_repr_gen(stats)
        print(ch, '  '.join(ch_stats_repr))

    lum_stats_repr = stats_repr_gen(lum_dev_stats)
    print('\nlum  ', '  '.join(lum_stats_repr))


def get_mismatch_points(ethalon, result, chid):
    im1 = Image.open(IMAGES_DIR + ethalon).split()
    im2 = Image.open(IMAGES_DIR + result).split()

    data = []
    idx = 0
    for c1, c2 in zip(im1[chid].tobytes(), im2[chid].tobytes()):
        if c1 != c2:
            data.append((idx, c1, c2))
        idx += 1

    return data

def verbose():
    channel_id = 'RGBA'.index(argv[4].upper())
    mismatch_points = get_mismatch_points(argv[1], argv[2], channel_id)

    background_bytes = Image.open(IMAGES_DIR + 'background.png').tobytes()
    active_bytes = Image.open(IMAGES_DIR + 'active.png').tobytes()

    print('Mismatch points for channel %s:\n\n'
          'index │ act  bg =>> exp got\n'
          '══════╪════════════════════' % argv[4].upper())
    for idx, c1, c2 in mismatch_points:
        idx = (idx << 2) + channel_id
        b = background_bytes[idx]
        a = active_bytes[idx]
        print('%5d │ %3d %3d =>> %3d %3d' % (idx >> 2, a, b, c1, c2))


if __name__ == '__main__':
    if len(argv) < 3:
        print('Deviation Info tool ─ Calculates deviation stats and'
              ' generates deviation maps.\n\n'
              'Usage: deviation_info.py <ethalon_image> <result_image>'
              ' [<map_base_name> | -v (R|G|B|A)]\n'
              '       NOTE: All file names are relative to "images" dir!\n\n'
              'Options:\n'
              '    -v (R|G|B|A), --verbose (R|G|B|A)   Print verbose'
              ' information about deviations for specified channel.')
        exit()

    if len(argv) >= 4 and argv[3] in ('-v', '--verbose'):
        verbose()
    else:
        main()
