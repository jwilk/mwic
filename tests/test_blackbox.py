# Copyright © 2014-2018 Jakub Wilk <jwilk@jwilk.net>
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

import errno
import glob
import io
import os
import sys
import unittest

import nose
from nose.tools import (
    assert_multi_line_equal,
)

import lib.cli as M

assert_multi_line_equal.__self__.maxDiff = None  # pylint: disable=no-member

here = os.path.dirname(__file__)
here = os.path.relpath(here)

def _get_output(path, language):
    binstdout = io.BytesIO()
    [old_stdout, old_argv] = [sys.stdout, sys.argv]
    try:
        sys.argv = ['mwic', '--language', language, path]
        textstdout = sys.stdout = io.TextIOWrapper(binstdout, encoding='UTF-8')
        try:
            try:
                M.main()
            except SystemExit as exc:
                if exc.code != 0:
                    raise
            sys.stdout.flush()
            return binstdout.getvalue().decode('UTF-8')
        finally:
            textstdout.close()
    finally:
        [sys.stdout, sys.argv] = [old_stdout, old_argv]

def _test_text(xpath):
    assert xpath.endswith('.exp')
    if '@' in xpath:
        [ipath, language] = xpath[:-4].rsplit('@')
    else:
        language = 'en-US'
        ipath = xpath[:-4]
    ipath += '.txt'
    text = _get_output(ipath, language)
    with open(xpath, 'rt', encoding='UTF-8') as file:
        expected = file.read()
    if expected != text:
        altxpath = xpath[:-4] + '.alt'
        try:
            file = open(altxpath, 'rt', encoding='UTF-8')
        except IOError as exc:
            if exc.errno == errno.ENOENT:
                pass
            else:
                raise
        else:
            with file:
                alt_expected = file.read()
            if alt_expected == text:
                expected = alt_expected
    assert_multi_line_equal(expected, text)

def test_text():
    for xpath in glob.glob(here + '/*.exp'):
        yield _test_text, xpath
test_text.redundant = True  # not needed if the plugin is enabled

class Plugin(nose.plugins.Plugin):

    name = 'mwic-plugin'
    enabled = True

    def options(self, parser, env):
        pass

    def wantFile(self, path):
        abs_here = os.path.abspath(here)
        abs_here = os.path.join(abs_here, '')
        if path.startswith(abs_here) and path.endswith('.exp'):
            return True

    def loadTestsFromFile(self, path):
        if self.wantFile(path):
            yield TestCase(path)

    def wantFunction(self, func):
        if getattr(func, 'redundant', False):
            return False

class TestCase(unittest.TestCase):

    def __init__(self, path):
        super().__init__('_test')
        self.path = os.path.relpath(path)

    def _test(self):
        _test_text(self.path)

    def __str__(self):
        return self.path

# vim:ts=4 sts=4 sw=4 et
