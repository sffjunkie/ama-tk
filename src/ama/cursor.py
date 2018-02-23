"""Terminal cursor control via ANSI escape sequences"""

import atexit
import sys

__all__ = ['toggle', 'show', 'hide']
_HIDDEN = False

def show():
    """Show the cursor"""
    sys.stdout.write('\u001b[?25h')
    _HIDDEN = False

def hide():
    """Hide the cursor"""
    sys.stdout.write('\u001b[?25l')
    _HIDDEN = True

def toggle(force=None):
    """Toggle the cursor"""
    if force is not None:
        _HIDDEN = force
    if _HIDDEN:
        show()
    else:
        hide()

atexit.register(show)
