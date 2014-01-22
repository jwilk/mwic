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

import argparse
import collections
import functools
import io
import sys

import enchant.tokenize

def ltrim(s, n, *, char='…'):
    if len(s) <= n:
        return s
    if n <= 1:
        return char
    return char + s[-n+1:]

def rtrim(s, n, *, char='…'):
    if len(s) <= n:
        return s
    if n <= 1:
        return char
    return s[:n-1] + char

class Occurrences(object):

    def __init__(self):
        self._data = collections.defaultdict(set)

    def add(self, word, line,  pos):
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', metavar='<file>', nargs='*', default=['-'])
    ap.add_argument('--language', metavar='<lang>', default='en')
    ap.add_argument('--input-encoding', metavar='<enc>', default='utf-8')
    ap.add_argument('--max-context-width', metavar='<n>', default=30)
    ap.add_argument('--suggest', metavar='<n>', type=int, default=0)
    options = ap.parse_args()
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, 'utf-8')
    try:
        split_words = enchant.tokenize.get_tokenizer(options.language)
    except enchant.errors.TokenizerNotFoundError:
        split_words = enchant.tokenize.get_tokenizer(None)
    dictionary = enchant.Dict(options.language)
    spellcheck = functools.lru_cache(maxsize=None)(
        dictionary.check
    )
    misspellings = Misspellings()
    for path in options.files:
        if path == '-':
            file = io.TextIOWrapper(sys.stdin.buffer, encoding=options.input_encoding)
        else:
            file = open(path, 'rt', encoding=options.input_encoding)
        with file:
            for line in file:
                line = line.strip()
                for word, pos in split_words(line):
                    if not spellcheck(word):
                        misspellings.add(word, line, pos)
    rare_misspellings = Misspellings()
    for word, occurrences in misspellings.sorted_words():
        if len(occurrences) == 1:
            [(word, line, positions)] = occurrences
            rare_misspellings.add(word, line, positions)
            continue
        extra = ''
        if options.suggest > 0:
            suggestions = dictionary.suggest(word)[:options.suggest]
            if suggestions:
                extra = ' ({sug})'.format(sug=', '.join(suggestions))
        print(word + extra + ':')
        occurrences = [
            (
                ltrim(lcontext, options.max_context_width),
                word,
                rtrim(rcontext, options.max_context_width),
            )
            for lcontext, word, rcontext
            in occurrences.sorted_context()
        ]
        lwidth = max(len(lcontext) for lcontext, _, _, in occurrences)
        rwidth = max(len(rcontext) for _, _, rcontext, in occurrences)
        for lcontext, word, rcontext in occurrences:
            print('| {lc:>{lw}}{word}{rc}{extra}'.format(
                lc=lcontext, lw=lwidth,
                word=word,
                rc=rcontext,
                extra=extra,
            ))
        print('', ' ' * lwidth, '^' * len(word))
        print()

    for line, occurrences in rare_misspellings.sorted_lines():
        header = []
        underline = bytearray(b' ' * len(line))
        for word, line, positions in sorted(occurrences):
            extra = ''
            if options.suggest > 0:
                suggestions = dictionary.suggest(word)[:options.suggest]
                if suggestions:
                    extra = ' ({sug})'.format(sug=', '.join(suggestions))
            header += [word + extra]
            for x in positions:
                underline[x : x + len(word)] = b'^' * len(word)
        print(', '.join(header) + ':')
        underline = underline.decode()
        lwidth = len(underline) - len(underline.lstrip())
        rwidth = len(underline) - len(underline.rstrip())
        lexceed = lwidth - options.max_context_width
        rexceed = rwidth - options.max_context_width
        if lexceed > 0:
            lwidth = len(line) - lexceed
            line = ltrim(line, lwidth)
            underline = ltrim(underline, lwidth, char=' ')
        if rexceed > 0:
            rwidth = len(line) - rexceed
            line = rtrim(line, rwidth)
            underline = rtrim(underline, rwidth, char=' ')
        print('|', line)
        print(' ', underline.rstrip())
        print()

if __name__ == '__main__':
    main()

# vim:ts=4 sw=4 et
