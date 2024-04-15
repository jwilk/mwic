# Copyright © 2015-2024 Jakub Wilk <jwilk@jwilk.net>
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

import io
import unittest.mock

from lib import colors as M

from .tools import (
    assert_equal,
)

def with_stdout(encoding):
    stdout = io.TextIOWrapper(
        io.BytesIO(),
        encoding=encoding,
    )
    return unittest.mock.patch('sys.stdout', stdout)

@with_stdout('UTF-8')
def test_control_characters():
    def t(s, x):
        r = M.escape(s)
        assert_equal(r, '\33[7m' + x + '\33[27m')
    t('\x00', '^@')
    t('\x01', '^A')
    t('\x02', '^B')
    t('\x03', '^C')
    t('\x04', '^D')
    t('\x05', '^E')
    t('\x06', '^F')
    t('\x07', '^G')
    t('\x08', '^H')
    t('\x09', '^I')
    t('\x0A', '^J')
    t('\x0B', '^K')
    t('\x0C', '^L')
    t('\x0D', '^M')
    t('\x0E', '^N')
    t('\x0F', '^O')
    t('\x10', '^P')
    t('\x11', '^Q')
    t('\x12', '^R')
    t('\x13', '^S')
    t('\x14', '^T')
    t('\x15', '^U')
    t('\x16', '^V')
    t('\x17', '^W')
    t('\x18', '^X')
    t('\x19', '^Y')
    t('\x1A', '^Z')
    t('\x1B', '^[')
    t('\x1C', '^\\')
    t('\x1D', '^]')
    t('\x1E', '^^')
    t('\x1F', '^_')
    t('\x7F', '^?')
    t('\x80', '<U+0080>')
    t('\x81', '<U+0081>')
    t('\x82', '<U+0082>')
    t('\x83', '<U+0083>')
    t('\x84', '<U+0084>')
    t('\x85', '<U+0085>')
    t('\x86', '<U+0086>')
    t('\x87', '<U+0087>')
    t('\x88', '<U+0088>')
    t('\x89', '<U+0089>')
    t('\x8A', '<U+008A>')
    t('\x8B', '<U+008B>')
    t('\x8C', '<U+008C>')
    t('\x8D', '<U+008D>')
    t('\x8E', '<U+008E>')
    t('\x8F', '<U+008F>')
    t('\x90', '<U+0090>')
    t('\x91', '<U+0091>')
    t('\x92', '<U+0092>')
    t('\x93', '<U+0093>')
    t('\x94', '<U+0094>')
    t('\x95', '<U+0095>')
    t('\x96', '<U+0096>')
    t('\x97', '<U+0097>')
    t('\x98', '<U+0098>')
    t('\x99', '<U+0099>')
    t('\x9A', '<U+009A>')
    t('\x9B', '<U+009B>')
    t('\x9C', '<U+009C>')
    t('\x9D', '<U+009D>')
    t('\x9E', '<U+009E>')
    t('\x9F', '<U+009F>')

@with_stdout('UTF-8')
def test_escape_safe():
    def t(s):
        r = M.escape(s)
        assert_equal(r, s)
    t('A')
    t('Á')

# vim:ts=4 sts=4 sw=4 et
