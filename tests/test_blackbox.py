# Copyright © 2014-2023 Jakub Wilk <jwilk@jwilk.net>
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

import glob
import io
import os
import random
import signal
import string
import sys
import unittest.mock

import lib.cli as M

from .tools import (
    assert_in,
    assert_multi_line_equal,
)

here = os.path.dirname(__file__)
here = os.path.relpath(here)

def _get_output(*args, stdin=''):
    argv = ['mwic', *args]
    binstdin = io.BytesIO(stdin.encode('UTF-8'))
    textstdin = io.TextIOWrapper(binstdin, encoding='UTF-8')
    binstdout = io.BytesIO()
    textstdout = io.TextIOWrapper(binstdout, encoding='UTF-8')
    sys_patch = unittest.mock.patch.multiple(sys, argv=argv, stdin=textstdin, stdout=textstdout)
    signal_patch = unittest.mock.patch('signal.signal')
    with sys_patch, signal_patch:
        try:
            try:
                M.main()
            except SystemExit as exc:
                if exc.code != 0:
                    raise
            signal.signal.assert_called_once()
            sys.stdout.flush()
            return binstdout.getvalue().decode('UTF-8')
        finally:
            textstdout.close()

def random_word():
    return str.join('', [
        random.choice(string.ascii_lowercase)
        for x in range(32)
    ])

def test_max_context_width():
    bad_word = random_word()
    text = _get_output('--language', 'en', '--max-context-width=2', stdin=f'yes {bad_word} yes')
    assert_in(f'… {bad_word} …', text)

def _test_text(xpath):
    assert xpath.endswith('.exp')
    if '@' in xpath:
        [ipath, language] = xpath[:-4].rsplit('@')
    else:
        language = 'en-US'
        ipath = xpath[:-4]
    ipath += '.txt'
    text = _get_output('--language', language, ipath)
    with open(xpath, 'rt', encoding='UTF-8') as file:
        expected = file.read()
    if expected != text:
        altxpath = xpath[:-4] + '.alt'
        try:
            file = open(altxpath, 'rt', encoding='UTF-8')  # pylint: disable=consider-using-with
        except FileNotFoundError:
            pass
        else:
            with file:
                alt_expected = file.read()
            if alt_expected == text:
                expected = alt_expected
    assert_multi_line_equal(expected, text)

class TestText(unittest.TestCase):

    def __str__(self):
        return self._testMethodName.split("'")[1]

    @classmethod
    def _add_test(cls, xpath):
        def method(self):
            del self
            return _test_text(xpath)
        name = f'test[{xpath!r}]'
        pytest = sys.modules.get('pytest')
        if pytest and int(pytest.__version__.split('.', 1)[0]) < 6:
            # pytest before 6.0 doesn't like "[" in the test name
            # https://github.com/pytest-dev/pytest/commit/8b9b81c3c04399d0
            name = name.replace('[', '(').replace(']', ')')
        method.__name__ = name
        setattr(cls, name, method)

    @classmethod
    def _add_tests(cls, xpaths):
        for xpath in xpaths:
            cls._add_test(xpath)

TestText._add_tests(glob.glob(here + '/*.exp'))  # pylint: disable=protected-access

def nose_plugin():

    import nose.plugins  # pylint: disable=import-outside-toplevel

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

        def wantClass(self, cls):
            return f'{cls.__module__}.{cls.__name__}' != 'tests.test_blackbox.TestText'

    class TestCase(unittest.TestCase):

        def __init__(self, path):
            super().__init__('_test')
            self.path = os.path.relpath(path)

        def _test(self):
            _test_text(self.path)

        def __str__(self):
            return self.path

    return Plugin()

# vim:ts=4 sts=4 sw=4 et
