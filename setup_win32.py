# This file is Python 2.7.
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
from glob import glob
import py2exe

sys.path.append('src')

try:
    distutils.dir_util.remove_tree("build")
    distutils.dir_util.remove_tree("dist")
except:
    pass

languages = ("de", "fr")
language_data_files = []
for language in languages:
    language_path = "po/" + language + "/LC_MESSAGES"
    language_data_files.append((language_path, ["po/" + language + "/felo.mo"]))

setup(name = 'Felo',
      windows = [{'script': 'src/felo.py',
                  'icon_resources': [(1, 'src/felo.ico')]}],
      description = 'Felo',
      version = '1.0.3',
      long_description = \
      """Felo ratings are a wonderful new method to estimate fencers.  The Felo
program calculates these ratings for a given group of fencers.  The
only thing the user needs to do is to provide the program with a
bout result list.  The program offers a graphical user interface (using wxWidgets).""",
      author = 'Torsten Bronger',
      author_email = 'bronger@physik.rwth-aachen.de',
      maintainer_email = 'felo-general@lists.sourceforge.net',
      url = 'http://felo.sourceforge.net',
      download_url = 'http://sourceforge.net/projects/felo/',
      keywords = 'fencing sports Felo rating',
      license = 'MIT License',
      options = {'py2exe': {'includes': 'felo_rating'}},
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
      platforms = "Linux, Windows",
      data_files = [('.', glob('src/auf*.dat') + glob('src/boilerplate*.felo') + glob('src/*.png') +
                     glob('src/licence*.html') + glob('*.ico'))]
      + language_data_files
)
