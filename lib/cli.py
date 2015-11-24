#!/usr/bin/python3

# Copyright © 2013-2015 Jakub Wilk <jwilk@jwilk.net>
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

__version__ = '0.2'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    ap.add_argument('files', metavar='<file>', nargs='*', default=['-'])
    ap.add_argument('-r', '--reverse', action='store_true')
    ap.add_argument('-l', '--language', metavar='<lang>', default='en')
    ap.add_argument('--list-languages', nargs=0, action=list_languages)
    ap.add_argument('--input-encoding', metavar='<enc>', default='utf-8:replace')
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
    encoding = options.input_encoding
    enc_errors = 'strict'
    if ':' in encoding:
        [encoding, enc_errors] = encoding.rsplit(':', 1)
    for path in options.files:
        if path == '-':
            file = io.TextIOWrapper(
                sys.stdin.buffer,
                encoding=encoding,
                errors=enc_errors,
            )
        else:
            file = open(
                path, 'rt',
                encoding=encoding,
                errors=enc_errors,
            )
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
    if options.reverse:
        print_rare_misspellings(rare_misspellings, options=options)
        print_common_misspellings(misspellings, options=options)
    else:
        print_common_misspellings(misspellings, options=options)
        print_rare_misspellings(rare_misspellings, options=options)

def print_common_misspellings(misspellings, *, options):
    sorted_words = misspellings.sorted_words()
    if options.reverse:
        sorted_words = reversed(sorted_words)
    for word, occurrences in sorted_words:
        if len(occurrences) == 1:
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
            print('| {lc:>{lw}}{word}{rc}'.format(
                lc=lcontext, lw=lwidth,
                word=word,
                rc=rcontext,
            ))
        print('', ' ' * lwidth, '^' * len(word))
        print()

def print_rare_misspellings(misspellings, *, options):
    for line, occurrences in misspellings.sorted_lines():
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

class list_languages(argparse.Action):
    def __call__(self, *args, **kwargs):
        for lang in sorted(enchant.list_languages()):
            print(lang)
        sys.exit(0)

# vim:ts=4 sts=4 sw=4 et
