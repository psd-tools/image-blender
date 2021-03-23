=============
image-blender
=============

``image-blender`` is a Python extension which provides a fast implementation of
Adobe Photoshop's blend modes. It is written using Cython. It was supposed to be
a helper module for psd-tools_ package back in 2015, but ended up in release hell
as I've lost an inspiration.

|Status| |PyPI|

.. _psd-tools: https://github.com/psd-tools/psd-tools

.. |Status| image:: https://img.shields.io/pypi/status/image-blender?label=Status
            :alt: Development status

.. |PyPI| image:: https://img.shields.io/pypi/v/image-blender?label=PyPI
          :target: https://pypi.org/project/image-blender/
          :alt: PyPI version

Usage
-----
``image-blender`` is not a complete solution, it only provides you with blend
functions themselves, so you can blend two images together. You should use some
additional Python package to work with images and alpha-composite them (e.g.
Pillow_ or pymaging_).

.. _Pillow: https://github.com/python-pillow/Pillow
.. _pymaging: https://github.com/ojii/pymaging

There are some requirements that should be met to apply a blend function to a
pair of images:

1. Blend functions work with bytes, so you must pass a raw image data into them;
2. Both images must be in ``RGBA`` mode and have the same size;
3. Both images must have a bit depth of 32 bits (8 bits per channel).

Let's take a look at some use cases, but first let's define one helper
function and make some preparations. From now on it's assumed you're using
Pillow and all of the above requirements are already met:

.. code:: python
   :number-lines:

   from PIL import Image
   import image_blender

   def apply_opacity(im, opacity):
       if opacity == 255:
           return im

       alpha_index = len(im.mode) - 1
       a = im.split()[alpha_index]
       opacity_scale = opacity / 255
       a = a.point(lambda i: i * opacity_scale)
       im.putalpha(a)
       return im

   image_bottom = Image.open("image1.png")
   image_top = Image.open("image2.png")

   opacity = 200

The above function applies a constant opacity to an image with existing
alpha channel. Now let's go to the examples:

* Blend two images using ``Normal`` mode with some opacity:

  .. code:: python
     :number-lines: 20

     # apply opacity to the top image first...
     image_top = apply_opacity(image_top, opacity)
     # ... then simply alpha-composite them, no blend function is needed...
     result = Image.alpha_composite(image_bottom, image_top)

     result.save("normal_with_opacity.png")

* Blend two images using ``Multiply`` mode (without opacity):

  .. code:: python
     :number-lines: 20

     # apply a blend function to a raw image data...
     tmp_top_bytes = image_blender.multiply(image_bottom.tobytes(), image_top.tobytes())
     # ... then create a new Image object from the resulting data...
     # Note: Images' sizes are the same.
     tmp_top = Image.frombytes("RGBA", image_top.size, tmp_top_bytes)
     # ... finally, alpha-composite a new top image with a bottom one...
     #
     # Note: In these examples images have an alpha channel.
     #       That's why we still need to alpha-composite them!
     result = Image.alpha_composite(image_bottom, tmp_top)

     result.save("multiply.png")

* Blend two images using ``Multiply`` mode with some opacity:

  .. code:: python
     :number-lines: 20

     # simply combine the above examples...
     image_top = apply_opacity(image_top, opacity)
     tmp_top_bytes = image_blender.multiply(image_bottom.tobytes(), image_top.tobytes())
     tmp_top = Image.frombytes("RGBA", image_top.size, tmp_top_bytes)
     result = Image.alpha_composite(image_bottom, tmp_top)

     result.save("multiply_with_opacity.png")

* Blend two images using ``Dissolve`` mode with some opacity:

  .. code:: python
     :number-lines: 20

     image_top = apply_opacity(image_top, opacity)
     result_bytes = image_blender.dissolve(image_bottom.tobytes(), image_top.tobytes())
     result = Image.frombytes("RGBA", image_top.size, result_bytes)
     # This one is a bit different here:
     # you should NOT alpha-composite the images when using Dissolve mode!

     result.save("dissolve_with_opacity.png")

License
-------
Copyright 2015-2021 Evgeny Kopylov. Licensed under the `MIT License`_.

.. _`MIT License`: https://github.com/psd-tools/image-blender/blob/master/LICENSE.txt
