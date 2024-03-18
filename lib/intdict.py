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

'''
internal dictionary, which can contain:
+ blacklist of multi-word misspellings;
+ whitelist of words that are commonly found in software code or documentation,
  but are not present in standard dictionaries.
'''

import os

import regex as re

basedir = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    os.path.pardir,
    '',
))
datadir = os.path.join(basedir, 'dict', '')

os.stat(datadir)

def _find_nothing(s):
    del s
    return ()

class Macros:

    def __init__(self):
        self._defs = {}
        self._regex = None
        self._substs = None

    def __setitem__(self, name, definition):
        if name in self._defs:
            raise KeyError(name)  # no coverage
        self._defs[name] = definition
        self._regex = None
        self._substs = None

    def expand(self, s):
        if not self._defs:
            return s
        if self._regex is not None:
            regex = self._regex
            substs = self._substs
        else:
            substs = []
            regex = []
            for i, (name, definition) in enumerate(self._defs.items()):
                substs += [definition]
                regex += [f'(?P<mwic{i}>{re.escape(name)})']
            regex = str.join('|', regex)
            regex = re.compile(regex)
            self._regex = regex
            self._substs = substs
        assert self._regex is not None
        assert self._substs is not None
        def replace(match):
            for i, subst in enumerate(substs):
                if match.group(f'mwic{i}') is not None:
                    return subst
            assert False  # no coverage
        return self._regex.sub(replace, s)

class Dictionary:

    def __init__(self, lang):
        self._whitelist = set()
        regexes = []
        lang = lang.lower().replace('_', '-')
        while True:
            path = os.path.join(datadir, lang)
            try:
                file = open(path, 'rt', encoding='UTF-8')  # pylint: disable=consider-using-with
            except FileNotFoundError:
                [lang, *suffix] = lang.rsplit('-', 1)
                if suffix:
                    continue
                else:
                    break
            macros = Macros()
            n = None  # hi, pylint
            def error(reason):  # no coverage
                return SyntaxError(reason, (file.name, n, 1, whole_line))
            with file:
                for n, line in enumerate(file, 1):
                    whole_line = line
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
                    elif line[0][0] == '@':
                        if (len(line) >= 4) and (line[0] == '@define') and (line[2] == '='):
                            (_, name, _, *definition) = line
                            definition = str.join(r'\s+', definition)
                            definition = fr'(?:{definition})'
                            try:
                                re.compile(definition)
                            except re.error as exc:  # no coverage
                                raise error(exc)
                            try:
                                macros[name] = macros.expand(definition)  # pylint: disable=unsubscriptable-object
                            except KeyError:  # no coverage
                                raise error(f'duplicate macro definition: {name}')
                        else:
                            raise error('malformed @-command')  # no coverage
                    else:
                        regex = str.join(r'\s+', line)
                        regex = macros.expand(regex)
                        try:
                            re.compile(regex)
                        except re.error as exc:  # no coverage
                            raise error(exc)
                        regexes += [regex]
            break
        if regexes:
            regex = str.join('|', regexes)
            regex = fr'\b(?:(?i){regex})\b'
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
