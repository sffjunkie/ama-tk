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

try:
    import colorama
    colorama.init(autoreset=True)
    COLOR = True
except:
    COLOR = False
    
def colorize(intensity, color, text):
    if COLOR:
        return colorama.Style.__dict__[intensity.upper()] + colorama.Fore.__dict__[color.upper()] + text
    else:
        return text

def create_color_func(intensity, name):
    def inner(text):
        return colorize(intensity, name, text)
    if intensity == 'normal':
        globals()[name] = inner
    else:
        globals()['%s_%s' % (intensity, name)] = inner

if COLOR:
    intensities = [x for x in colorama.Style.__dict__.keys() if x!='RESET_ALL']
    colours = [x for x in colorama.Fore.__dict__.keys() if x!='RESET']
else:
    intensities = ['DIM', 'NORMAL', 'BRIGHT']
    colours = ['BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE']

for intensity in intensities:
    for fore in colours:
        create_color_func(intensity.lower(), fore.lower())
