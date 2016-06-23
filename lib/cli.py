# Copyright © 2013-2016 Jakub Wilk <jwilk@jwilk.net>
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
import lib.extdict
import lib.intdict
import lib.ns
import lib.pager
import lib.text

__version__ = '0.7'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', action='version', version='%(prog)s {}'.format(__version__))
    ap.add_argument('files', metavar='FILE', nargs='*', default=['-'])
    ap.add_argument('-l', '--language', metavar='LANG', default='en')
    ap.add_argument('--list-languages', nargs=0, action=list_languages)
    ap.add_argument('--blacklist', metavar='FILE', action='append', default=[])
    ap.add_argument('--camel-case', action='store_true')
    ap.add_argument('--input-encoding', metavar='ENC', default='UTF-8:replace')
    default_output_format = 'color' if sys.stdout.isatty() else 'plain'
    ap.add_argument('-f', '--output-format', choices=('plain', 'color'), default=default_output_format)
    ap.add_argument('-r', '--reverse', action='store_true')
    ap.add_argument('--compact', action='store_true')
    ap.add_argument('--limit', metavar='N', type=int, default=1e999)
    ap.add_argument('--max-context-width', metavar='N', default=30)
    ap.add_argument('--suggest', metavar='N', type=int, default=0)
    options = ap.parse_args()
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, 'UTF-8')
    try:
        split_words = enchant.tokenize.get_tokenizer(options.language)
    except enchant.errors.TokenizerNotFoundError:
        split_words = enchant.tokenize.get_tokenizer(None)
    if options.camel_case:
        split_words = lib.text.camel_case_tokenizer(split_words)
    if options.language == 'und':
        dictionary = None
        spellcheck = ''.__gt__  # always returns False
        options.suggest = 0
    else:
        dictionary = enchant.Dict(options.language)
        spellcheck = functools.lru_cache(maxsize=None)(
            dictionary.check
        )
    intdict = lib.intdict.Dictionary(options.language)
    extdict = lib.extdict.Dictionary(*options.blacklist)
    misspellings = lib.data.Misspellings()
    encoding = options.input_encoding
    enc_errors = 'strict'
    if ':' in encoding:
        [encoding, enc_errors] = encoding.rsplit(':', 1)
    ctxt = lib.ns.Namespace(
        dictionary=dictionary,
        intdict=intdict,
        extdict=extdict,
        split_words=split_words,
        spellcheck=spellcheck,
        misspellings=misspellings,
        options=options,
    )
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
            spellcheck_file(ctxt, file)
    if not misspellings:
        return
    raw_cc = options.output_format == 'color'
    with lib.pager.autopager(raw_control_chars=raw_cc):
        print_misspellings(ctxt)

def spellcheck_file(ctxt, file):
    force_ucs2 = (
        ctxt.dictionary is not None and
        ctxt.dictionary.provider.name == 'myspell'
    )
    for line in file:
        if force_ucs2:
            # https://github.com/rfk/pyenchant/issues/58
            line = ''.join(c if c <= '\uFFFF' else '\uFFFD' for c in line)
        line = line.strip()
        line = line.expandtabs()
        taken = bytearray(len(line))
        for word, pos in ctxt.split_words(line):
            if word in ctxt.extdict:
                certainty = 1
            elif ctxt.spellcheck(word):
                continue
            elif ctxt.intdict.is_whitelisted(word):
                continue
            else:
                certainty = 0
            for i, ch in enumerate(word, start=pos):
                taken[i] = True
            ctxt.misspellings.add(word, line, pos, certainty)
        for word, pos in ctxt.intdict.find(line):
            for i, ch in enumerate(word, start=pos):
                if taken[i]:
                    break
            else:
                ctxt.misspellings.add(word, line, pos, 1)

def print_misspellings(ctxt):
    rare_misspellings = lib.data.Misspellings()
    for word, occurrences in ctxt.misspellings.sorted_words():
        if len(occurrences) == 1:
            [(word, line, positions)] = occurrences
            for pos, certainty in positions.items():
                rare_misspellings.add(word, line, pos, certainty)
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
        highlight_color = 'error' if occurrences.certainty > 0 else 'warn'
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
                word = lib.colors.highlight(word, highlight_color)
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
        if not options.compact:
            print()

def print_rare_misspellings(ctxt):
    options = ctxt.options
    use_color = options.output_format == 'color'
    for line, occurrences in ctxt.rare_misspellings.sorted_lines(reverse=options.reverse):
        header = []
        underline = bytearray(b' ' * len(line))
        for word, line, positions in sorted(occurrences):
            if use_color and (max(positions.values()) > 0):
                underline_char = b'!'
            else:
                underline_char = b'^'
            if len(positions) > options.limit:
                continue
            extra = ''
            if options.suggest > 0:
                suggestions = ctxt.dictionary.suggest(word)[:options.suggest]
                if suggestions:
                    extra = ' ({sug})'.format(sug=', '.join(suggestions))
            header += [word + extra]
            for x in positions:
                underline[x : x + len(word)] = underline_char * len(word)
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
        if use_color:
            hline = lib.colors.highlight(
                line, (
                    'warn' if u == '^' else
                    'error' if u == '!' else
                    'off'
                    for u in underline
                )
            )
            print(lib.colors.dim('|'), hline)
        else:
            print('|', line)
            print(' ', underline.rstrip())
        if not options.compact:
            print()

class list_languages(argparse.Action):
    def __call__(self, *args, **kwargs):
        for lang in sorted(enchant.list_languages()):
            print(lang)
        sys.exit(0)

__all__ = ['main']

# vim:ts=4 sts=4 sw=4 et
