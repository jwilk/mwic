# Copyright © 2015-2016 Jakub Wilk <jwilk@jwilk.net>
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
internal dictionary, which can contain:
+ blacklist of multi-word misspellings;
+ whitelist of words that are commonly found in software code or documentation,
  but are not present in standard dictionaries.
'''

import errno
import os

import regex as re

basedir = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    '',
))
datadir = os.path.join(basedir, 'dict', '')

os.stat(datadir)

def _find_nothing(s):  # pylint: disable=unused-argument
    return ()

class Dictionary(object):

    def __init__(self, lang):
        self._whitelist = set()
        regexes = []
        lang = lang.lower().replace('_', '-')
        while True:
            path = os.path.join(datadir, lang)
            try:
                file = open(path, 'rt', encoding='UTF-8')
            except IOError as exc:
                if exc.errno != errno.ENOENT:
                    raise
                [lang, *suffix] = lang.rsplit('-', 1)
                if suffix:
                    continue
                else:
                    break
            with file:
                for line in file:
                    if line.startswith('#'):
                        continue
                    line = line.split()
                    if not line:
                        continue
                    if line[0] == '*':
                        [word] = line[1:]
                        self._whitelist.add(word)
                        self._whitelist.add(word.upper())
                        self._whitelist.add(word.title())
                    else:
                        regexes += [
                            r'\s+'.join(line)
                        ]
            break
        if regexes:
            regex = r'\b(?:(?i){0})\b'.format(
                '|'.join(regexes)
            )
            self._find = re.compile(regex).finditer
        else:
            self._find = _find_nothing

    def find(self, s):
        for match in self._find(s):
            yield (match.group(), match.start())

    def is_whitelisted(self, word):
        return word in self._whitelist

__all__ = ['Dictionary']

# vim:ts=4 sts=4 sw=4 et
