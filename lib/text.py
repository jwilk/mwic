# Copyright © 2013-2023 Jakub Wilk <jwilk@jwilk.net>
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
text manipulation functions
'''

import functools
import regex as re

def ltrim(s, n, *, char='…'):
    if n <= 0:
        return s and char
    pat = re.compile(r'\X\X(\X{#})\Z'.replace('#', str(n - 1)))
    match = pat.search(s)
    if match is None:
        return s
    if n <= 1:
        return char
    return char + match.group(1)

def rtrim(s, n, *, char='…'):
    if n <= 0:
        return s and char
    pat = re.compile(r'\A(\X{#})\X\X'.replace('#', str(n - 1)))
    match = pat.match(s)
    if match is None:
        return s
    if n <= 1:
        return char
    return match.group(1) + char

_camel_case_split = re.compile('([A-Z][^A-Z]*)').split

def camel_case_tokenizer(tokenizer):
    @functools.wraps(tokenizer)
    def new_tokenizer(s):
        for word, offset in tokenizer(s):
            if word.isupper():
                yield word, offset
                continue
            for subword in _camel_case_split(word):
                if subword:
                    yield subword, offset
                offset += len(subword)
    return new_tokenizer

__all__ = [
    'camel_case_tokenizer',
    'ltrim',
    'rtrim',
]

# vim:ts=4 sts=4 sw=4 et
