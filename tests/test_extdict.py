# Copyright © 2016-2022 Jakub Wilk <jwilk@jwilk.net>
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

import contextlib
import functools
import tempfile

import lib.extdict as M

from .tools import (
    assert_in,
    assert_not_in,
)


@contextlib.contextmanager
def tmpdict(data):
    with tempfile.NamedTemporaryFile(prefix='mwic.', suffix='.txt', mode='wt', encoding='ASCII') as file:
        file.write(data)
        file.flush()
        yield file.name

def _test_dict(bad, good, *, d):
    if not isinstance(good, set):
        raise TypeError
    if not isinstance(bad, set):
        raise TypeError
    for word in bad:
        assert_in(word, d)
    for word in good:
        assert_not_in(word, d)

lintian_dict = '''\
# All spelling errors that have been observed "in the wild" in package
# descriptions are added here, ...
#
# Please keep the list sorted (using the en_US locale).

abandonned||abandoned
portugese||Portuguese
upto||up to
'''
def test_lintian():
    with tmpdict(lintian_dict) as path:
        d = M.Dictionary(path)
    t = functools.partial(_test_dict, d=d)
    t({'abandonned', 'Abandonned', 'ABANDONNED'}, {'abandoned'})
    t({'portugese', 'Portugese', 'PORTUGESE'}, {'Portuguese'})
    t({'upto', 'Upto', 'UPTO'}, {'up to'})

lintian_case_dict = '''\
# Picky corrections, applied before lowercasing the word. ...
#
# Please keep the list sorted (using the en_US locale).

american||American
Debian-Edu||Debian Edu
SLang||S-Lang
'''

def test_lintian_case():
    with tmpdict(lintian_case_dict) as path:
        d = M.Dictionary(path)
    t = functools.partial(_test_dict, d=d)
    t({'american'}, {'American', 'AMERICAN'})
    t({'Debian-Edu'}, {'Debian Edu', 'debian-edu', 'DEBIAN-EDU'})
    t({'SLang'}, {'S-Lang', 'slang', 'SLANG'})

codespell_dict = '''\
abandonned->abandoned
clas->class, disabled because of name clash in c++
intented->intended, indented,
'''

def test_codespell():
    with tmpdict(codespell_dict) as path:
        d = M.Dictionary(path)
    t = functools.partial(_test_dict, d=d)
    t({'abandonned', 'Abandonned', 'ABANDONNED'}, {'abandoned'})
    t({'clas', 'Clas', 'CLAS'}, {'class'})
    t({'intented', 'Intented', 'INTENTED'}, {'intended', 'indented'})

kde_dict = '''\
#! /usr/bin/env perl

# CORRECTIONS GO IN THE __DATA__ SECTION AT THE END OF THIS SCRIPT

# Checks and corrects common spelling errors in text files - ...

__DATA__

#INCORRECT SPELLING    CORRECTION

aasumes                assumes

#INCORRECT SPELLING    CORRECTION

Addtional              Additional
'''

def test_kde():
    with tmpdict(kde_dict) as path:
        d = M.Dictionary(path)
    t = functools.partial(_test_dict, d=d)
    t({'aasumes'}, {'assumes'})  # FIXME? 'assumes'
    t({'Addtional'}, {'Additional'})  # FIXME? 'addtional'

plain_dict = '''\
abandonned
Portugese
'''

def test_plain():
    with tmpdict(plain_dict) as path:
        d = M.Dictionary(path)
    t = functools.partial(_test_dict, d=d)
    t({'abandonned', 'Abandonned', 'ABANDONNED'}, {'abandoned'})
    t({'Portugese'}, {'portugese', 'PORTUGESE'})

# vim:ts=4 sts=4 sw=4 et
