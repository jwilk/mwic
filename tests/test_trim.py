# Copyright © 2014-2024 Jakub Wilk <jwilk@jwilk.net>
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

import regex

import lib.text as M

from .tools import (
    assert_equal,
    assert_greater_equal,
)

def xlen(s):
    n = sum(1 if c else 0 for c in regex.split(r'(\X)', s))
    if s.isascii():
        assert n == len(s)
    else:
        assert n <= len(s)
    return n

def test_ltrim():
    def t(s, n, expected):
        result = M.ltrim(s, n)
        assert_equal(result, expected)
        assert_greater_equal(
            max(1, n),
            xlen(result)
        )
    t('', 0, '')
    truncations = [
        '…',
        '…',
        '…s',
        '…gs',
        'eggs',
        'eggs',
    ]
    for n, s in enumerate(truncations):
        t(truncations[-1], n, s)
    truncations = [
        s.replace('g', 'g\N{COMBINING GRAVE ACCENT}')
        for s in truncations
    ]
    for n, s in enumerate(truncations):
        t(truncations[-1], n, s)

def test_rtrim():
    def t(s, n, expected):
        result = M.rtrim(s, n)
        assert_equal(result, expected)
        assert_greater_equal(
            max(1, n),
            xlen(result)
        )
    t('', 0, '')
    truncations = [
        '…',
        '…',
        'e…',
        'eg…',
        'eggs',
        'eggs',
    ]
    for n, s in enumerate(truncations):
        t(truncations[-1], n, s)
    truncations = [
        s.replace('g', 'g\N{COMBINING ACUTE ACCENT}')
        for s in truncations
    ]
    for n, s in enumerate(truncations):
        t(truncations[-1], n, s)

# vim:ts=4 sts=4 sw=4 et
