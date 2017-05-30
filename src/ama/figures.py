import re
import sys

__all__ = ['figures', 'FIGURES']

MAIN = {
    'tick': '✔',
    'cross': '✖',
    'star': '★',
    'square': '▇',
    'squareSmall': '◻',
    'squareSmallFilled': '◼',
    'play': '▶',
    'circle': '◯',
    'circleFilled': '◉',
    'circleDotted': '◌',
    'circleDouble': '◎',
    'circleCircle': 'ⓞ',
    'circleCross': 'ⓧ',
    'circlePipe': 'Ⓘ',
    'circleQuestionMark': '?⃝',
    'bullet': '●',
    'dot': '․',
    'line': '─',
    'ellipsis': '…',
    'pointer': '❯',
    'pointerSmall': '›',
    'info': 'ℹ',
    'warning': '⚠',
    'hamburger': '☰',
    'smiley': '㋡',
    'mustache': '෴',
    'heart': '♥',
    'arrowUp': '↑',
    'arrowDown': '↓',
    'arrowLeft': '←',
    'arrowRight': '→',
    'radioOn': '◉',
    'radioOff': '◯',
    'checkboxOn': '☒',
    'checkboxOff': '☐',
    'checkboxCircleOn': 'ⓧ',
    'checkboxCircleOff': 'Ⓘ',
    'questionMarkPrefix': '?⃝',
    'oneHalf': '½',
    'oneThird': '⅓',
    'oneQuarter': '¼',
    'oneFifth': '⅕',
    'oneSixth': '⅙',
    'oneSeventh': '⅐',
    'oneEighth': '⅛',
    'oneNinth': '⅑',
    'oneTenth': '⅒',
    'twoThirds': '⅔',
    'twoFifths': '⅖',
    'threeQuarters': '¾',
    'threeFifths': '⅗',
    'threeEighths': '⅜',
    'fourFifths': '⅘',
    'fiveSixths': '⅚',
    'fiveEighths': '⅝',
    'sevenEighths': '⅞'
}

WIN32 = {
    'tick': '√',
    'cross': '×',
    'star': '*',
    'square': '█',
    'squareSmall': '[ ]',
    'squareSmallFilled': '[█]',
    'play': '►',
    'circle': '( )',
    'circleFilled': '(*)',
    'circleDotted': '( )',
    'circleDouble': '( )',
    'circleCircle': '(○)',
    'circleCross': '(×)',
    'circlePipe': '(│)',
    'circleQuestionMark': '(?)',
    'bullet': '*',
    'dot': '.',
    'line': '─',
    'ellipsis': '...',
    'pointer': '>',
    'pointerSmall': '»',
    'info': 'i',
    'warning': '‼',
    'hamburger': '≡',
    'smiley': '☺',
    'mustache': '┌─┐',
    'heart': MAIN['heart'],
    'arrowUp': MAIN['arrowUp'],
    'arrowDown': MAIN['arrowDown'],
    'arrowLeft': MAIN['arrowLeft'],
    'arrowRight': MAIN['arrowRight'],
    'radioOn': '(*)',
    'radioOff': '( )',
    'checkboxOn': '[×]',
    'checkboxOff': '[ ]',
    'checkboxCircleOn': '(×)',
    'checkboxCircleOff': '( )',
    'questionMarkPrefix': '？',
    'oneHalf': '1/2',
    'oneThird': '1/3',
    'oneQuarter': '1/4',
    'oneFifth': '1/5',
    'oneSixth': '1/6',
    'oneSeventh': '1/7',
    'oneEighth': '1/8',
    'oneNinth': '1/9',
    'oneTenth': '1/10',
    'twoThirds': '2/3',
    'twoFifths': '2/5',
    'threeQuarters': '3/4',
    'threeFifths': '3/5',
    'threeEighths': '3/8',
    'fourFifths': '4/5',
    'fiveSixths': '5/6',
    'fiveEighths': '5/8',
    'sevenEighths': '7/8'
}

if 'linux' in sys.platform:
    # the main one doesn't look that good on Ubuntu
    MAIN['questionMarkPrefix'] = '?'

FIGURES = WIN32 if 'win32' in sys.platform else MAIN

class Figures():
    """Container for Figures"""
    def __init__(self):
        self._translate = FIGURES is WIN32

    def __call__(self, string):
        if not self._translate:
            return string
        else:
            for key, value in MAIN.items():
                if value == FIGURES[key]:
                    continue
                else:
                    string = re.sub(re.escape(MAIN[key]), WIN32[key], string)

    def __getattr__(self, key):
        return FIGURES[key]

figures = Figures()
