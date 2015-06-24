#!/usr/bin/python3

# Copyright © 2013, 2014 Jakub Wilk <jwilk@jwilk.net>
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

import collections
import sys

class Occurrences(object):

    def __init__(self):
        self._data = collections.defaultdict(set)

    def add(self, word, line, pos):
        if isinstance(pos, int):
            self._data[(word, line)].add(pos)
        else:
            self._data[(word, line)] |= pos

    def count(self):
        return sum(
            len(positions)
            for positions in self._data.values()
        )

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for (word, line), positions in self._data.items():
            yield word, line, positions

    @staticmethod
    def _sorting_key(item):
        lcontext, word, rcontext = item
        return (rcontext, lcontext[::-1], word)

    def _context(self):
        for (word, line), positions in self._data.items():
            for pos in positions:
                lcontext = line[:pos]
                rcontext = line[pos + len(word):]
                yield lcontext, word, rcontext

    def sorted_context(self):
        return sorted(self._context(), key=self._sorting_key)

class Misspellings(object):

    def __init__(self):
        self._word_index = collections.defaultdict(Occurrences)
        self._line_index = collections.defaultdict(Occurrences)

    def add(self, word, line, pos):
        word = sys.intern(word)
        line = sys.intern(line)
        self._word_index[word].add(word, line, pos)
        self._line_index[line].add(word, line, pos)

    @staticmethod
    def _sorting_key(item):
        s, occurrences = item
        return -occurrences.count(), s

    def sorted_words(self):
        return sorted(
            self._word_index.items(),
            key=self._sorting_key
        )

    def sorted_lines(self):
        return sorted(
            self._line_index.items(),
            key=self._sorting_key
        )

# vim:ts=4 sts=4 sw=4 et
