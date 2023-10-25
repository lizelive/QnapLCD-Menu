"""
A simplistic package and examples using the front panel display and buttons
on QNAP NAS devices under other operating systems. Tested with TVS-671,
but should work on other models that use the "A125" display with two buttons.
"""
from .driver import QnapLCD
from .cli import qnaplcd as main
