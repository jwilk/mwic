# Copyright © 2016-2024 Jakub Wilk <jwilk@jwilk.net>
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
external misspelling dictionary

Supported dictionary formats:
+ Lintian
  - <https://salsa.debian.org/lintian/lintian/raw/master/data/spelling/corrections>
  - <https://salsa.debian.org/lintian/lintian/raw/master/data/spelling/corrections-case>
+ codespell <https://github.com/codespell-project/codespell/raw/master/codespell_lib/data/dictionary.txt>
+ kde-spellcheck <https://github.com/KDE/kde-dev-scripts/raw/master/kde-spellcheck.pl>
+ plain word list
'''

import re

separators = {
    '||',  # Lintian
    '->',  # codespell
}

def case_variants(word, correction=None):
    yield word
    if not word.islower():
        return
    correction = correction or ''
    if word.title() != correction.title():
        yield word.title()
    if word.upper() != correction.upper():
        yield word.upper()

def parse_line(line):
    word = line
    for sep in separators:
        try:
            [word, correction] = line.split(sep, 1)
        except ValueError:
            pass
        else:
            break
    else:
        correction = None
    return case_variants(word, correction)

class Dictionary:

    def __init__(self, *paths):
        self._dict = set()
        for path in paths:
            self._read(path)

    def __contains__(self, word):
        return word in self._dict

    def _add(self, word):
        self._dict.add(word)

    def _read(self, path):
        with open(path, 'rt', encoding='UTF-8') as file:
            self._read_fp(file)

    def _read_fp(self, file):
        add = self._add
        kde = None
        for line in file:
            if kde is None:
                kde = re.match(r'\A#!.*\bperl\b', line)
                if kde:
                    return self._read_fp_kde(file)
            if line[:1] == '#':
                continue
            line = line.strip()
            if not line:
                continue
            for word in parse_line(line):
                add(word)

    def _read_fp_kde(self, file):
        add = self._add
        for line in file:
            if line.strip() == '__DATA__':
                break
        for line in file:
            if line[:1] == '#':
                continue
            line = line.split()
            if line:
                add(line[0])

__all__ = ['Dictionary']

# vim:ts=4 sts=4 sw=4 et
