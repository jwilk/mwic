# Copyright © 2016 Jakub Wilk <jwilk@jwilk.net>
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
import re
import sys

import nose
from nose.tools import (
    assert_equal,
)

here = os.path.dirname(__file__)
basedir = '{here}/..'.format(here=here)

def find_files(root, ext):
    suffix = '.' + ext
    for root, dirs, files in os.walk(root):
        for path in files:
            if not path.endswith(suffix):
                continue
            path = os.path.join(root, path)
            path = os.path.relpath(path)
            yield path

def test_rst():
    def t(path):
        try:
            import docutils.core
        except ImportError as exc:
            raise nose.SkipTest(exc)
        try:
            with open(path, 'rb') as file:
                docutils.core.publish_file(file, settings_overrides=dict(
                    input_encoding='UTF-8',
                    output_encoding='UTF-8',
                    report_level=999,
                    halt_level=0,
                    warning_stream=os.devnull,
                ))
        except docutils.utils.SystemMessage as exc:
            match = re.match(r'\A([^\s:]+):(\d+): (.+)', str(exc))
            if match is None:
                raise
            msg_path, n, msg = match.groups()
            n = int(n)
            assert_equal(msg_path, path)
            with open(path, 'rt', encoding='UTF-8', errors='replace') as file:
                for m, line in enumerate(file, 1):
                    if n == m:
                        break
                else:
                    line = ''
            if sys.version_info >= (3, 3):
                exc = None
            raise SyntaxError(msg, (path, n, 1, line)) from exc
    for path in find_files(basedir, ext='rst'):
        yield t, path

# vim:ts=4 sts=4 sw=4 et
