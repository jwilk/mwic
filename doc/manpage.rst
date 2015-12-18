====
mwic
====

---------------------------
Misspelled Words In Context
---------------------------

:manual section: 1
:version: mwic 0.4.1
:date: |date|

Synopsis
--------
**mwic** [-l *lang*] [*option*...] [*file*...]

Description
-----------
**mwic** is a spell-checking frontend that groups misspellings and shows them in their contexts.
This is useful for checking technical documents that often contain words that are not included in standard dictionaries.


Options
-------

-l lang, --language lang
   Spell-check for this language.
   The default is ``en``.

--list-languages
   Print list of available languages.

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

--limit n
   Assume that words that occurred more than *n* times are spelled correctly.

--max-context-width n
   Limit context width to *n* characters.
   The default is 30.

--suggest n
   Suggest up to *n* corrections.

-h, --help
   Show the help message and exit.

--version
   Show the program's version number and exit.

Environment
-----------

PAGER
   If stdout is a terminal, mwic pipes the output through ``$PAGER``.
   The default is ``pager``.

LESS
   If this variable is unset, mwic sets it
   to ``FX``,
   or to ``FXR`` if the output is in color.

LV
   If this variable in unset, and the output is in color,
   mwic sets this variable to ``-c``.

Example
-------

::

   $ mwic debian-social-contract.txt
   GPL:
   | The "GPL", "BSD", and "Artistic" lice…
          ^^^

   contrib:
   | created "contrib" and "non-free" areas in our…
              ^^^^^^^

   CDs:
   | their CDs. Thus, although non-free wor…
           ^^^

   Ean, Schuessler:
   | community" was suggested by Ean Schuessler. This document was drafted
                                 ^^^ ^^^^^^^^^^

   DFSG:
   | …an Free Software Guidelines (DFSG)
   | …an Free Software Guidelines (DFSG) part of the
                                   ^^^^

   Perens:
   |    Bruce Perens later removed the Debian-spe…
   | by Bruce Perens, refined by the other Debian…
              ^^^^^^

.. |date| date:: %Y-%m-%d

.. vim:ts=3 sts=3 sw=3
