# Copyright © 2015-2019 Jakub Wilk <jwilk@jwilk.net>
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

'''
color terminal support
'''

import io
import itertools
import unicodedata

class _seq:
    dim = '\x1B[90m'
    off = '\x1B[0m'
    warn = '\x1B[30;43m'
    error = '\x1B[30;41m'
    reverse = '\x1B[7m'
    unreverse = '\x1B[27m'

def dim(s):
    return _seq.dim + escape(s) + _seq.off

def escape(s):
    return highlight(s, itertools.repeat('off'))

def highlight(s, w):
    if isinstance(w, str):
        w = itertools.repeat(w)
    fp = io.StringIO()
    off = _seq.off
    old_color = off
    for (cs, cw) in zip(s, w):
        color = getattr(_seq, cw)
        if color != old_color:
            fp.write(color)
            old_color = color
        if unicodedata.category(cs) == 'Cc':
            if cs < ' ' or cs == '\x7F':
                cs = '^' + chr(ord(cs) ^ ord('@'))
            else:
                cs = '<U+{0:04X}>'.format(ord(cs))
            cs = '{t.reverse}{c}{t.unreverse}'.format(c=cs, t=_seq)
        fp.write(cs)
    if old_color != off:
        fp.write(off)
    return fp.getvalue()

__all__ = [
    'dim',
    'escape',
    'highlight',
]

# vim:ts=4 sts=4 sw=4 et
