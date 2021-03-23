import pytest

from .utils import full_name, tobytes, frombytes
from PIL import Image, ImageMath
import image_blender


DEV_STATS_PER_MODE = (
    ('dissolve',        (True,  False,  -127,   +128,   20000)),

    ('darken',          (True,  True,   None,   None,   None )),
    ('multiply',        (True,  True,   None,   None,   None )),
    ('color_burn',      (True,  True,   None,   None,   None )),
    ('linear_burn',     (True,  True,   None,   None,   None )),
    ('darker_color',    (False, False,  -1,     0,      39999)),

    ('lighten',         (True,  True,   None,   None,   None )),
    ('screen',          (True,  True,   None,   None,   None )),
    ('color_dodge',     (True,  True,   None,   None,   None )),
    ('linear_dodge',    (True,  True,   None,   None,   None )),
    ('lighter_color',   (False, True,   None,   None,   None )),

    ('overlay',         (True,  True,   None,   None,   None )),
    ('soft_light',      (True,  False,  -1,     +1,     37902)),
    ('hard_light',      (True,  False,  0,      +1,     29706)),
    ('vivid_light',     (True,  False,  0,      +128,   37630)),
    ('linear_light',    (True,  False,  0,      +1,     20794)),
    ('pin_light',       (True,  False,  0,      +1,     32942)),
    ('hard_mix',        (True,  True,   None,   None,   None )),

    ('difference',      (True,  True,   None,   None,   None )),
    ('exclusion',       (True,  False,  -1,     +1,     33224)),
    ('subtract',        (True,  True,   None,   None,   None )),
    ('divide',          (True,  True,   None,   None,   None )),

    ('hue',             (False, False,  0,      +1,     39800)),
    ('saturation',      (False, False,  0,      +1,     39800)),
    ('color',           (False, False,  0,      +1,     39800)),
    ('luminosity',      (False, False,  -2,     0,      39909))
)


def _make_deviation_map(ch1, ch2):
    return ImageMath.eval('127 + ch2 - ch1', ch1=ch1, ch2=ch2).convert('L')

def _make_luminance_map(bands):
    return ImageMath.eval(
        '(30*r + 59*g + 11*b + 50) / 100',
        r=bands[0], g=bands[1], b=bands[2]
    ).convert('L')

def _get_color_stats(ch):
    return dict((c, n) for n, c in ch.getcolors())

def _get_deviations_channels(im1, im2):
    im1 = im1.split()[:3]
    im2 = im2.split()[:3]

    ch_dev_maps = [x for x in map(_make_deviation_map, im1, im2)]
    ch_dev_stats = [x for x in map(_get_color_stats, ch_dev_maps)]

    return ch_dev_stats

def _get_deviations_luminance(im1, im2):
    im1 = im1.split()
    im2 = im2.split()

    lum_dev_map = _make_deviation_map(
        _make_luminance_map(im1), _make_luminance_map(im2)
    )

    return _get_color_stats(lum_dev_map)


def _ethalon_generator():
    ethalon_results = Image.open(full_name('basics', 'ethalon_results.png'))

    for i in range(len(DEV_STATS_PER_MODE)):
        y = i // 7 * 200
        x = i % 7 * 200
        bbox = (x, y, x + 200, y + 200)
        yield ethalon_results.crop(bbox)

image1_bytes = tobytes( Image.open(full_name('basics', 'image1.png')) )
image2_bytes = tobytes( Image.open(full_name('basics', 'image2.png')) )

ethalon_result = _ethalon_generator()


@pytest.mark.parametrize(('func_name', 'dev_stats'), DEV_STATS_PER_MODE)
def test_blend_modes_basics(func_name, dev_stats):
    (is_separable, is_precise,
        deviation_neg, deviation_pos, match_count) = dev_stats

    ethalon = next(ethalon_result)
    blend_func = getattr(image_blender, func_name)
    result_bytes = blend_func(image1_bytes, image2_bytes)
    result = frombytes('RGBA', (200, 200), result_bytes)

    if is_separable:
        deviations = _get_deviations_channels(ethalon, result)

        if is_precise:
            for channel_deviations in deviations:
                assert len(channel_deviations) == 1
                assert 127 in channel_deviations
        else:
            ch_dev_values = (sorted(ch_devs.keys()) for ch_devs in deviations)
            dvals_r, dvals_g, dvals_b = ch_dev_values
            min_deviation_value = min(dvals_r[ 0], dvals_g[ 0], dvals_b[ 0])
            max_deviation_value = max(dvals_r[-1], dvals_g[-1], dvals_b[-1])

            assert max_deviation_value - 127 == deviation_pos
            assert min_deviation_value - 127 == deviation_neg

            for channel_deviations in deviations:
                assert channel_deviations[127] >= match_count
    else:
        deviations = _get_deviations_luminance(ethalon, result)

        if is_precise:
            assert len(deviations) == 1
            assert 127 in deviations
        else:
            lum_dev_values = sorted(deviations.keys())
            assert lum_dev_values[-1] - 127 == deviation_pos
            assert lum_dev_values[ 0] - 127 == deviation_neg

            assert deviations[127] >= match_count


def test_blend_with_transparent():
    image1 = Image.open(full_name('blend_with_transparent', 'image1.png'))
    image2 = Image.open(full_name('blend_with_transparent', 'image2.png'))
    ethalon = Image.open(full_name('blend_with_transparent', 'ethalon.png'))

    ethalon_bytes = tobytes(ethalon)
    result_bytes = image_blender.multiply(tobytes(image1), tobytes(image2))

    assert len(ethalon_bytes) == len(result_bytes)
    assert ethalon_bytes == result_bytes
