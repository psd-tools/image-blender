#!/usr/bin/env python
from setuptools import setup
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.egg_info import egg_info
from setuptools.command.sdist import sdist
from distutils import errors

import os
import sys


# ========================== copied from coverage.py ==========================

# A replacement for the build_ext command which raises a single exception
# if the build fails, so we can fallback nicely.

ext_errors = (
    errors.CCompilerError,
    errors.DistutilsExecError,
    errors.DistutilsPlatformError,
    # distutils.msvc9compiler can raise an IOError when failing to find
    # the compiler
    IOError
)


class BuildFailed(Exception):
    """Raise this to indicate the C extension wouldn't build."""

    def __init__(self, exc):
        Exception.__init__(self)
        self.name = exc.__class__.__name__
        self.cause = str(exc)


class build_ext_ex(build_ext):
    """Builds C extensions, but fails with a straightforward exception."""

    def run(self):
        """Wrap `run` with `BuildFailed`."""

        try:
            build_ext.run(self)
        except errors.DistutilsPlatformError as e:
            raise BuildFailed(e)

    def build_extension(self, ext):
        """Wrap `build_extension` with `BuildFailed`."""

        if self.compiler.compiler_type == 'msvc':
            # enforce full optimization; default compiler flags are sub-optimal
            ext.extra_compile_args.append('/O2')

        try:
            # Uncomment to test compile failures:
            # raise errors.CCompilerError('OOPS')

            build_ext.build_extension(self, ext)
        except ext_errors as e:
            raise BuildFailed(e)
        except ValueError as e:
            # this can happen on Windows 64-bit, see Python issue 7511
            if "'path'" in str(e):
                raise BuildFailed(e)
            raise

# =============================================================================


class egg_info_ex(egg_info):
    """Includes license file into `.egg-info` folder."""

    def run(self):
        # don't duplicate license into `.egg-info` when building a distribution
        if not self.distribution.have_run.get('install', True):
            # `install` command is in progress, copy license
            self.mkpath(self.egg_info)
            self.copy_file('LICENSE.txt', self.egg_info)

        egg_info.run(self)


class sdist_fix(sdist):
    """
    Stores only basename of a `.tar` file in GZIP archive, not its path.
    Python issue 41316 workaround.
    """

    def make_archive(self, base_name, format, base_dir, owner, group):
        if format == 'gztar':
            base_name += '.tar.gz'
            if not self.dry_run and os.path.exists(base_name):
                os.remove(base_name)

            self.mkpath(self.dist_dir)
            sdist.make_archive(
                self, base_dir, format, None, base_dir, owner, group
            )
            return self.move_file(base_dir + '.tar.gz', base_name)

        return sdist.make_archive(
            self, base_name, format, None, base_dir, owner, group
        )


def get_long_description():
    f = open('README.rst', 'rt')
    info = f.read()
    f.close()
    return info

def main():
    """Actually invokes setup() with the arguments below."""

    # There are a few reasons we might not be able to compile the C extensions.
    # Let's figure out if we should attempt to build extensions or not.
    if sys.platform.startswith('java'):
        sys.exit("**\n** Jython can't compile C extensions!\n**")

    if '__pypy__' in sys.builtin_module_names:
        sys.exit('**\n** Cython extensions are slow under PyPy.\n**')

    setup_args = dict(
        name = 'image-blender',
        version = '0.1.0',
        author = 'Evgeny Kopylov',
        url = 'https://github.com/psd-tools/image-blender',

        description = ("Python extension which provides a fast implementation"
                       " of Adobe Photoshop's blend modes"),
        long_description = get_long_description(),
        keywords = ('photoshop,layers,images,blending,composition,'
                    'chops,imagechops'),
        license = 'MIT License',

        zip_safe = False,

        ext_modules = [
            Extension('image_blender', ['src/image_blender.c'])
        ],
        license_files = ('LICENSE.txt',),
        cmdclass = {
            'build_ext': build_ext_ex, 'egg_info': egg_info_ex,
            'sdist': sdist_fix
        },

        classifiers = (
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Cython',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: Implementation :: CPython',
            'Topic :: Multimedia :: Graphics',
            'Topic :: Multimedia :: Graphics :: Editors',
            'Topic :: Multimedia :: Graphics :: Editors :: Raster-Based',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules'
        )
    )

    # For a variety of reasons, it might not be possible to install the
    # C extensions. Try to install and abort with message if it fails.
    try:
        setup(**setup_args)
    except BuildFailed as exc:
        sys.exit('**\n** Failed to build an extension!\n** %s: %s\n**' % (
            exc.name, exc.cause
        ))


if __name__ == '__main__':
    main()
