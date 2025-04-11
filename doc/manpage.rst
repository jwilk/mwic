====
mwic
====

---------------------------
Misspelled Words In Context
---------------------------

:manual section: 1
:version: mwic 0.7.11
:date: 2023-08-25

Synopsis
--------
**mwic** [-l *lang*] [*option*...] [*file*...]

Description
-----------
**mwic** is a spell-checker that groups possible misspellings and shows them in their contexts.
This is useful for checking technical documents,
which often contain words that are not included in standard dictionaries.


Options
-------

-l lang, --language lang
   Spell-check for this language.
   The default is ``en``.

--list-languages
   Print list of available languages.

--blacklist file
   Treat words from the external dictionary as misspelled.
   The dictionary can be in the format used by *Lintian*,
   or in the format used by *codespell*,
   or in the format used by *kde-spellcheck* (part of *kde-dev-scripts*);
   or it can be plain newline-separated word list.
   This option can be used multiple times.

--camel-case
   Split camel-cased compound words.
   For example, treat “eggBaconAndSpam” as 4 separate words.

--input-encoding enc
   Assume this input encoding.
   The default is ``UTF-8:replace``
   (UTF-8 encoding
   with error handler replacing malformed characters with U+FFFD).

-f fmt, --output-format fmt
   If *fmt* is ``plain``,
   output plain text verbatim and highlight misspellings with the ``^`` character.
   This is the default if stdout is not a terminal.

   If *fmt* is ``color``,
   escape control characters and highlight misspellings with colors.
   This is the default if stdout is a terminal.

-r, --reverse
   Print words in reverse order,
   that is, the most common words first.

--compact
   Omit blank lines in output.

--limit n
   Assume that words that occurred more than *n* times are spelled correctly.

--max-context-width n
   Limit context width to *n* characters.
   The default is 30.

--suggest n
   Suggest up to *n* corrections.

-h, --help
   Show help message and exit.

--version
   Show version information and exit.

Environment
-----------

PAGER
   If stdout is a terminal, mwic pipes the output through ``$PAGER``.
   The default is ``pager`` (if it exists) or ``more``.
   Setting ``PAGER`` to the empty string or the value ``cat``
   disables the use of the pager.

LESS
   If this variable is unset, mwic sets it
   to ``-FX``,
   or to ``-FXR`` if the output is in color.

LV
   If this variable in unset, and the output is in color,
   mwic sets this variable to ``-c``.

Files
-----

Spell-checking can be eased by using dictionaries of commonly misspelled words.
**mwic** doesn't ship with one,
but it can use a number of dictionaries from third-party projects:

* Lintian:

  | https://salsa.debian.org/lintian/lintian/raw/master/data/spelling/corrections
  | https://salsa.debian.org/lintian/lintian/raw/master/data/spelling/corrections-case

* Linux kernel:

  | https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/plain/scripts/spelling.txt

* codespell:

  | https://github.com/codespell-project/codespell/raw/master/codespell_lib/data/dictionary.txt

* kde-dev-scripts:

  | https://github.com/KDE/kde-dev-scripts/raw/master/kde-spellcheck.pl

Example
-------

::

   $ mwic --blacklist /usr/share/lintian/data/spelling/corrections --compact rfc1927.txt
   heirarchical:
   | …g paper clips vs small ones; heirarchical assembly
                                   ^^^^^^^^^^^^
   multipart:
   | …tes the degree of binding of multipart documents:
                                   ^^^^^^^^^
   reycled:
   | 1) staples could be reycled for a small credit
                         ^^^^^^^

*...*

::

   EMail, edu, isi:
   | EMail: rogers@isi.edu
     ^^^^^         ^^^ ^^^
   electonic:
   | drawer of the electonic desk on home PCs
   |            3) electonic staples should have a standa…
                   ^^^^^^^^^


See also
--------

**spellintian**\ (1),
**codespell**\ (1);

“English for software localisation”
<http://jbr.me.uk/linux/esl.html>
by Justin B Rye

.. vim:ts=3 sts=3 sw=3
