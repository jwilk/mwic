# Copyright © 2012-2022 Jakub Wilk <jwilk@jwilk.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os

from lib.cli import __version__

from .tools import (
    assert_equal,
)

here = os.path.dirname(__file__)
docdir = os.path.join(here, os.pardir, 'doc')

def test_changelog():
    path = os.path.join(docdir, 'changelog')
    with open(path, 'rt', encoding='UTF-8') as file:
        line = file.readline()
    changelog_version = line.split()[1].strip('()')
    assert_equal(changelog_version, __version__)

def test_manpage():
    path = os.path.join(docdir, 'manpage.rst')
    manpage_version = None
    with open(path, 'rt', encoding='UTF-8') as file:
        for line in file:
            if line.startswith(':version:'):
                manpage_version = line.split()[-1]
                break
    assert_equal(manpage_version, __version__)

# vim:ts=4 sts=4 sw=4 et
