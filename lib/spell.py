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
spell-checking with parallelism and caching
'''

import concurrent.futures

class SpellChecker(object):

    def __init__(self, backend, njobs=1):
        self._backend = backend
        if njobs > 1:
            self._executor = concurrent.futures.ProcessPoolExecutor(max_workers=njobs)
        else:
            self._executor = None
        self._cache = {}
        self._queue = set()

    def queue(self, word):
        if word not in self._cache:
            self._queue.add(word)

    def check(self, word):
        self.queue(word)
        if self._queue:
            self._flush_queue()
        return self._cache[word]

    def _flush_queue(self):
        cache = self._cache
        check = self._backend
        if self._executor is not None and len(self._queue) > 1:
            queue = list(self._queue)
            for word, result in zip(queue, self._executor.map(check, queue)):
                cache[word] = result
        else:
            for word in self._queue:
                cache[word] = check(word)
        self._queue.clear()

class DummySpellChecker(object):

    def __init__(self):
        pass

    def queue(self, word):
        pass

    def check(self, word):
        return False

__all__ = [
    'SpellChecker',
    'DummySpellChecker',
]

# vim:ts=4 sts=4 sw=4 et
