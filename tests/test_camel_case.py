# Copyright © 2016-2022 Jakub Wilk <jwilk@jwilk.net>
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

import lib.text as M

from .tools import (
    assert_equal,
)

def naive_tokenizer(s):
    offset = 0
    for word in s.split():
        yield (word, offset)
        offset += len(word) + 1

tokenize = M.camel_case_tokenizer(naive_tokenizer)

def test_tokenizer():
    s = 'bacon eggAndSpam EggBaconAndSpam spamSPAM SPAM'
    r = list(tokenize(s))
    assert_equal(r, [
        ('bacon', 0),
        ('egg', 6),
        ('And', 9),
        ('Spam', 12),
        ('Egg', 17),
        ('Bacon', 20),
        ('And', 25),
        ('Spam', 28),
        ('spam', 33),
        ('S', 37),
        ('P', 38),
        ('A', 39),
        ('M', 40),
        ('SPAM', 42),
    ])
    w = r[-1]
    assert_equal(
        len(w[0]) + w[1],
        len(s)
    )

# vim:ts=4 sts=4 sw=4 et
