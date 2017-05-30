# Copyright 2009-2014, Simon Kennedy, sffjunkie+code@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
import sys
import os.path
from setuptools import setup

def read(*names, **kwargs):
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get("encoding", "utf8")
    ).read()

setup(name='ama',
    version='0.2',
    description="""Module to ask a set of questions from the user and return a set of answers.""",
    long_description=read('README'),
    author='Simon Kennedy',
    author_email='sffjunkie+code@gmail.com',
    url="https://launchpad.net/asker",
    license='Apache-2.0',
    package_dir={'': 'src'},
    py_modules=['ama.terminal', 'ama.tk', 'ama.validator'],
	install_requires=['babel', 'cerberus', 'tks'],
    extras_require={
        'color': ['colorama'],
        'date_picker': ['tks'],
        'time_picker': ['tks'],
    },
)
