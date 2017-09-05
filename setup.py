# encoding=UTF-8

# Copyright © 2016-2017 Jakub Wilk <jwilk@jwilk.net>
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
This setup script is only for pip.
Do not use directly.
'''

import distutils
import glob
import sys

...  # Python 3 is required

if 'setuptools' not in sys.modules:
    raise RuntimeError(' '.join(__doc__.strip().splitlines()))

def get_version():
    with open('doc/changelog', 'rt', encoding='UTF-8') as file:
        line = file.readline()
    return line.split()[1].strip('()')

distutils.core.setup(
    name='mwic',
    version=get_version(),
    license='MIT License',
    description='Misspelled Words In Context',
    url='http://jwilk.net/software/mwic',
    author='Jakub Wilk',
    author_email='jwilk@jwilk.net',
    packages=['_mwic', '_mwic.lib'],
    package_dir={'_mwic': ''},
    package_data={'_mwic': ['dict/*']},
    data_files=[('share/man/man1', glob.glob('doc/*.1'))],
    entry_points=dict(
        console_scripts=['mwic = _mwic.lib.cli:main']
    ),
    install_requires=['pyenchant', 'regex'],
)

# vim:ts=4 sts=4 sw=4 et
