The following software is needed to run mwic:

* Python ≥ 3.2;

* PyEnchant_, Python bindings for the Enchant_ spellchecking system;

* regex_, alternative regular expression module for Python.

Additionally, the following software is needed to rebuild the manual page from
source:

* docutils_ ≥ 0.6.


For pip users::

   python3 -m pip install pyenchant regex
   python3 -m pip install docutils

For Debian users::

   apt-get install python3-enchant python3-regex
   apt-get install python3-docutils


.. _regex:
   https://pypi.python.org/pypi/regex
.. _pyenchant:
   https://pypi.python.org/pypi/pyenchant
.. _Enchant:
   https://abiword.github.io/enchant/
.. _docutils:
   http://docutils.sourceforge.net/

.. vim:ts=3 sts=3 sw=3
