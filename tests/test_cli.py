# Copyright © 2019-2022 Jakub Wilk <jwilk@jwilk.net>
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

import argparse
import io
import unittest.mock

import lib.cli

from .tools import (
    assert_equal,
    assert_is_instance,
    assert_not_equal,
)

def test_version_action():
    action = lib.cli.VersionAction(['--version'])
    stdout = io.StringIO()
    ap = argparse.ArgumentParser()
    with unittest.mock.patch('sys.stdout', stdout):
        try:
            action(ap, None, None)
            raise SystemExit(...)
        except SystemExit as exc:
            assert_equal(exc.code, 0)
    s = stdout.getvalue()
    assert_is_instance(s, str)
    assert_not_equal(s, '')

# vim:ts=4 sts=4 sw=4 et
