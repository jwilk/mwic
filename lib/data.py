# Copyright © 2013-2024 Jakub Wilk <jwilk@jwilk.net>
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
collecting misspelling data
'''

import collections
import sys

class Occurrences:

    def __init__(self):
        self._data = collections.defaultdict(dict)
        self.certainty = 0

    def add(self, word, line, pos, certainty):
        if isinstance(pos, int):
            self._data[(word, line)][pos] = certainty
        else:
            for p in pos:
                self._data[(word, line)][p] = certainty
        self.certainty = max(self.certainty, certainty)

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

class Misspellings:

    def __init__(self):
        self._word_index = collections.defaultdict(Occurrences)
        self._line_index = collections.defaultdict(Occurrences)

    def add(self, word, line, pos, certainty):
        word = sys.intern(word)
        line = sys.intern(line)
        self._word_index[word].add(word, line, pos, certainty)
        self._line_index[line].add(word, line, pos, certainty)

    @staticmethod
    def _sorting_key(*, reverse=False):
        sign = 1
        if reverse:
            sign = -1
        def k(item):
            s, occurrences = item
            return (
                sign * -occurrences.certainty,
                sign * occurrences.count(),
                s
            )
        return k

    def __bool__(self):
        return bool(self._word_index)

    def sorted_words(self, *, reverse=False):
        return sorted(
            self._word_index.items(),
            key=self._sorting_key(reverse=reverse)
        )

    def sorted_lines(self, *, reverse=False):
        return sorted(
            self._line_index.items(),
            key=self._sorting_key(reverse=reverse)
        )

__all__ = [
    'Misspellings',
    'Occurrences',
]

# vim:ts=4 sts=4 sw=4 et
