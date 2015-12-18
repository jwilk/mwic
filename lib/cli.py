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

'''
the command-line interface
'''

import argparse
import io
import sys
import functools

import enchant.tokenize

import lib.colors
import lib.data
import lib.ns
import lib.pager
import lib.text

__version__ = '0.4.1'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    ap.add_argument('files', metavar='<file>', nargs='*', default=['-'])
    ap.add_argument('-l', '--language', metavar='<lang>', default='en')
    ap.add_argument('--list-languages', nargs=0, action=list_languages)
    ap.add_argument('--input-encoding', metavar='<enc>', default='utf-8:replace')
    default_output_format = 'color' if sys.stdout.isatty() else 'plain'
    ap.add_argument('-f', '--output-format', choices=('plain', 'color'), default=default_output_format)
    ap.add_argument('-r', '--reverse', action='store_true')
    ap.add_argument('--limit', type=int, default=1e999)
    ap.add_argument('--max-context-width', metavar='<n>', default=30)
    ap.add_argument('--suggest', metavar='<n>', type=int, default=0)
    options = ap.parse_args()
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, 'utf-8')
    try:
        split_words = enchant.tokenize.get_tokenizer(options.language)
    except enchant.errors.TokenizerNotFoundError:
        split_words = enchant.tokenize.get_tokenizer(None)
    dictionary = enchant.Dict(options.language)
    force_ucs2 = dictionary.provider.name == 'myspell'
    spellcheck = functools.lru_cache(maxsize=None)(
        dictionary.check
    )
    misspellings = lib.data.Misspellings()
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
                if force_ucs2:
                    # https://github.com/rfk/pyenchant/issues/58
                    line = ''.join(c if c <= '\uFFFF' else '\uFFFD' for c in line)
                line = line.strip()
                line = line.expandtabs()
                for word, pos in split_words(line):
                    if not spellcheck(word):
                        misspellings.add(word, line, pos)
    if not misspellings:
        return
    ctxt = lib.ns.Namespace(
        dictionary=dictionary,
        misspellings=misspellings,
        options=options,
    )
    with lib.pager.autopager(raw_control_chars=(options.output_format == 'color')):
        print_misspellings(ctxt)

def print_misspellings(ctxt):
    rare_misspellings = lib.data.Misspellings()
    for word, occurrences in ctxt.misspellings.sorted_words():
        if len(occurrences) == 1:
            [(word, line, positions)] = occurrences
            rare_misspellings.add(word, line, positions)
    ctxt.rare_misspellings = rare_misspellings
    if ctxt.options.reverse:
        print_common_misspellings(ctxt)
        print_rare_misspellings(ctxt)
    else:
        print_rare_misspellings(ctxt)
        print_common_misspellings(ctxt)

def print_common_misspellings(ctxt):
    options = ctxt.options
    for word, occurrences in ctxt.misspellings.sorted_words(reverse=options.reverse):
        if len(occurrences) == 1:
            continue
        if occurrences.count() > options.limit:
            continue
        extra = ''
        if options.suggest > 0:
            suggestions = ctxt.dictionary.suggest(word)[:options.suggest]
            if suggestions:
                extra = ' ({sug})'.format(sug=', '.join(suggestions))
        print(word + extra + ':')
        occurrences = [
            (
                lib.text.ltrim(lcontext, options.max_context_width),
                word,
                lib.text.rtrim(rcontext, options.max_context_width),
            )
            for lcontext, word, rcontext
            in occurrences.sorted_context()
        ]
        lwidth = max(len(lcontext) for lcontext, _, _, in occurrences)
        for lcontext, word, rcontext in occurrences:
            lcontext = lcontext.rjust(lwidth)
            if options.output_format == 'color':
                lcontext = lib.colors.escape(lcontext)
                word = lib.colors.highlight(word)
                rcontext = lib.colors.escape(rcontext)
                print(lib.colors.dim('|'), end=' ')
            else:
                print('|', end=' ')
            print('{lc}{word}{rc}'.format(
                lc=lcontext,
                word=word,
                rc=rcontext,
            ))
        if options.output_format != 'color':
            print('', ' ' * lwidth, '^' * len(word))
        print()

def print_rare_misspellings(ctxt):
    options = ctxt.options
    for line, occurrences in ctxt.rare_misspellings.sorted_lines(reverse=options.reverse):
        header = []
        underline = bytearray(b' ' * len(line))
        for word, line, positions in sorted(occurrences):
            if len(positions) > options.limit:
                continue
            extra = ''
            if options.suggest > 0:
                suggestions = ctxt.dictionary.suggest(word)[:options.suggest]
                if suggestions:
                    extra = ' ({sug})'.format(sug=', '.join(suggestions))
            header += [word + extra]
            for x in positions:
                underline[x : x + len(word)] = b'^' * len(word)
        if not header:
            continue
        print(', '.join(header) + ':')
        underline = underline.decode()
        lwidth = len(underline) - len(underline.lstrip())
        rwidth = len(underline) - len(underline.rstrip())
        lexceed = lwidth - options.max_context_width
        rexceed = rwidth - options.max_context_width
        if lexceed > 0:
            lwidth = len(line) - lexceed
            line = lib.text.ltrim(line, lwidth)
            underline = lib.text.ltrim(underline, lwidth, char=' ')
        if rexceed > 0:
            rwidth = len(line) - rexceed
            line = lib.text.rtrim(line, rwidth)
            underline = lib.text.rtrim(underline, rwidth, char=' ')
        if options.output_format == 'color':
            hline = lib.colors.highlight(
                line,
                (c != ' ' for c in underline),
            )
            print(lib.colors.dim('|'), hline)
            print()
        else:
            print('|', line)
            print(' ', underline.rstrip())
        print()

class list_languages(argparse.Action):
    def __call__(self, *args, **kwargs):
        for lang in sorted(enchant.list_languages()):
            print(lang)
        sys.exit(0)

__all__ = ['main']

# vim:ts=4 sts=4 sw=4 et
