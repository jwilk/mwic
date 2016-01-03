Print blacklisted words earlier than dictionary misspellings.

Add support for third-party blacklists:

* `Lintian <https://anonscm.debian.org/cgit/lintian/lintian.git/tree/data/spelling/corrections>`_

* `codespell <https://github.com/lucasdemarchi/codespell/blob/master/data/dictionary.txt>`_

* `kde-spellcheck <https://github.com/KDE/kde-dev-scripts/blob/master/kde-spellcheck.pl>`_

Whitelist the following English words,
which are commonly found in software code or documentation,
but are not present in dictionaries::

   backend
   backends
   boolean
   booleans
   endian
   endianness
   executable
   executables
   filename
   filenames
   filesystem
   filesystems
   natively
   prepend
   prepended
   prepending
   prepends
   tuple
   tuples

Whitelist long hex strings.

Whitelist long base64 strings.

Spell-check camel-cased words.

.. vim:ts=3 sts=3 sw=3
