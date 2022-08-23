# Copyright © 2012-2019 Jakub Wilk <jwilk@jwilk.net>
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

PYTHON = python3

PREFIX = /usr/local
DESTDIR =

bindir = $(PREFIX)/bin
basedir = $(PREFIX)/share/mwic
mandir = $(PREFIX)/share/man

.PHONY: all
all: ;

python_exe = $(shell $(PYTHON) -c 'import sys; print(sys.executable)')

.PHONY: install
install: mwic
	$(PYTHON) - < lib/__init__.py  # Python version check
	# executable:
	install -d $(DESTDIR)$(bindir)
	sed \
		-e "1 s@^#!.*@#!$(python_exe)@" \
		-e "s#^basedir = .*#basedir = '$(basedir)/'#" \
		$(<) > $(<).tmp
	install $(<).tmp $(DESTDIR)$(bindir)/$(<)
	rm $(<).tmp
	# library + data:
	install -d $(DESTDIR)$(basedir)/dict
	install -p -m644 dict/* $(DESTDIR)$(basedir)/dict/
	install -d $(DESTDIR)$(basedir)/lib
	install -p -m644 lib/*.py $(DESTDIR)$(basedir)/lib/
	umask 022 && $(PYTHON) -m compileall -q -d $(basedir)/lib $(DESTDIR)$(basedir)/lib
ifeq "$(wildcard doc/*.1)" ""
	# run "$(MAKE) -C doc" to build the manpage
else
	# manual page:
	install -d $(DESTDIR)$(mandir)/man1
	install -p -m644 doc/$(<).1 $(DESTDIR)$(mandir)/man1/
endif

.PHONY: test
test:
	$(PYTHON) -bb -m pytest -v

.PHONY: clean
clean:
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache
	rm -f .coverage
	rm -f *.tmp

.error = GNU make is required

# vim:ts=4 sts=4 sw=4 noet
