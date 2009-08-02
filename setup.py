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

from DistUtilsExtra.command import *

setup(name = 'felo',
      description = 'Calculate Felo ratings for estimating sport fencers',
      version = '1.0.2',
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
      options = {'bsdist_rpm': { 'release': '1', 'provides': 'felo', 'requires': 'python >= 2.4' }},
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
      data_files = [('/usr/bin', ["src/felo"]), ('/usr/share/pixmaps/', ["src/felo-icon.png"]),
                    ('/usr/share/applications/', ["src/felo.desktop"]),
                    ('/usr/share/info', ["doc/felo.info"] + ["doc/felo-screen-%d.png" % i for i in range(1, 7)])],
      platforms = "Linux, Windows",
      packages = ['felo'],
      package_dir = {'felo': 'src'},
      package_data = {'felo': ['auf*.dat', 'boilerplate*.felo', 'licence*.html', '*.png']},
      cmdclass = {"build": build_extra.build_extra, "build_i18n": build_i18n.build_i18n}
      )
