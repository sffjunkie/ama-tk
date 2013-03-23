# Copyright 2009-2013, Simon Kennedy, code@sffjunkie.co.uk
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

from distutils.core import setup

setup(name='ama',
    version='0.1',
    description="""Module to ask a set of questions from the user and return a set of answers""",
    author='Simon Kennedy',
    author_email='code@sffjunkie.co.uk',
    url="http://www.sffjunkie.co.uk/python-ama.html",
    license='Apache-2.0',
    py_modules=['ama.terminal', 'ama.tk', 'ama.validator', 'ama.color'],
    extras_require={'color': ['colorama']}
)
