#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    setup.py - Distutils setup script for Felo
#
#    Copyright © 2006 Torsten Bronger <bronger@physik.rwth-aachen.de>,
#
#    This file is part of the Felo program.
#
#    Felo is free software; you can redistribute it and/or modify it under
#    the terms of the MIT licence:
#
#    Permission is hereby granted, free of charge, to any person obtaining a
#    copy of this software and associated documentation files (the "Software"),
#    to deal in the Software without restriction, including without limitation
#    the rights to use, copy, modify, merge, publish, distribute, sublicense,
#    and/or sell copies of the Software, and to permit persons to whom the
#    Software is furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in
#    all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import distutils.dir_util
import shutil, os.path, atexit, sys

try:
    distutils.dir_util.remove_tree("build")
except:
    pass

# The following code may be very specific to my own home configuration,
# although I hope that it's useful to other who try to create Felo packages,
# too.
#
# The goal is to override an existing local RPM configuration.  Distutils only
# works together with a widely untouched configuration, so I have to disable
# any extisting one represented by the file ~/.rpmmacros.  I look for this file
# and move it to ~/.rpmmacros.original.  After setup.py is terminated, this
# renaming is reverted.
#
# Additionally, if a file ~/.rpmmacros.distutis exists, it is used for
# ~/.rpmmacros while setup.py is running.  So you can still make use of things
# like "%vendor" or "%packager".

home_dir = os.environ['HOME']
real_rpmmacros_name = os.path.join(home_dir, '.rpmmacros')
distutils_rpmmacros_name = os.path.join(home_dir, '.rpmmacros.distutils')
temp_rpmmacros_name = os.path.join(home_dir, '.rpmmacros.original')

def restore_rpmmacros():
    shutil.move(temp_rpmmacros_name, real_rpmmacros_name)

# I check whether temp_rpmmacros_name exists for two reasons: First, I don't
# want to overwrite it, and secondly, I don't want this renaming to take place
# twice.  This would happen otherwise, because setup.py is called more than
# once per building session.
if os.path.isfile(real_rpmmacros_name) and not os.path.isfile(temp_rpmmacros_name):
    shutil.move(real_rpmmacros_name, temp_rpmmacros_name)
    if os.path.isfile(distutils_rpmmacros_name):
        shutil.copy(distutils_rpmmacros_name, real_rpmmacros_name)
    atexit.register(restore_rpmmacros)

languages = ("de",)
language_data_files = []
for language in languages:
    language_path = os.path.join("share", "locale", language, "LC_MESSAGES")
    language_data_files.append((language_path, [os.path.join("/home/bronger/src/felo/po", language, "felo.mo")]))

setup(name = 'felo',
      description = 'Calculate Felo ratings for estimating sport fencers',
      version = '1.0',
      long_description = \
      """Felo ratings are a wonderful new method to estimate fencers.  The
Felo program calculates these ratings for a given group of fencers.
The only thing the user needs to do is to provide the program with a
bout result list.  The program offers a graphical user interface
(using wxWidgets).""",
      author = 'Torsten Bronger',
      author_email = 'bronger@physik.rwth-aachen.de',
      maintainer_email = 'felo-general@lists.sourceforge.net',
      url = 'http://felo.sourceforge.net',
      download_url = 'http://sourceforge.net/projects/felo/',
      keywords = 'fencing sports Felo rating',
      license = 'MIT License',
      options = {'bsdist_rpm': { 'release': '1', 'provides': 'felo', 'requires': 'python >= 2.4' },
                 'install': { 'prefix': '/usr' }
                 },
      classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Non-Profit Organizations',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
      data_files = language_data_files + [('bin', ["/home/bronger/src/felo/src/felo"])],
      platforms = "Linux, Windows",
      packages = ['felo'],
      package_dir = {'felo': 'src'},
      package_data = {'felo': ['auf*.dat', 'boilerplate*.felo', '*.png',
                      'licence*.html', '*.ico']}
      )
