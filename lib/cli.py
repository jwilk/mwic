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
import io
import sys
import functools

import enchant.tokenize

import lib.text as libtext
import lib.data as libdata

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', metavar='<file>', nargs='*', default=['-'])
    ap.add_argument('-l', '--language', metavar='<lang>', default='en')
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
    misspellings = libdata.Misspellings()
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
    rare_misspellings = libdata.Misspellings()
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
                libtext.ltrim(lcontext, options.max_context_width),
                word,
                libtext.rtrim(rcontext, options.max_context_width),
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
            line = libtext.ltrim(line, lwidth)
            underline = libtext.ltrim(underline, lwidth, char=' ')
        if rexceed > 0:
            rwidth = len(line) - rexceed
            line = libtext.rtrim(line, rwidth)
            underline = libtext.rtrim(underline, rwidth, char=' ')
        print('|', line)
        print(' ', underline.rstrip())
        print()

# vim:ts=4 sw=4 et
