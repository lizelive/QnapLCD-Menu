import platform
from .driver import QnapLCD
from .menu import menu

import click

@click.group()
def qnaplcd():
    "A simple cli to control qnap lcd"
    pass

menu = qnaplcd.command()(menu)

@qnaplcd.command()
def plugins():
    import sys
    if sys.version_info < (3, 10):
        from importlib_metadata import entry_points
    else:
        from importlib.metadata import entry_points

    discovered_plugins = entry_points(group=f'{__package__}.plugins')
    click.echo(discovered_plugins)

@qnaplcd.command()
def off():
    "turn off the lcd"
    lcd = QnapLCD()
    lcd.backlight(False)
    lcd.reset()
    lcd.clear()

@qnaplcd.command()
def preinit():
    "a short pre-initialization script to print a message on the LCD panel and terminate."
    lcd = QnapLCD()
    lcd.backlight(True)
    lcd.reset()
    lcd.clear()
    lcd.write(0, [platform.node(), 'Initializing...'])

@qnaplcd.command()
def postinit():
    "a short post-initialization script to print a message on the LCD panel and terminate. Not used in most cases."
    lcd = QnapLCD()
    lcd.backlight(True)
    lcd.reset()
    lcd.clear()
    lcd.write(0, [platform.node(), 'System Ready...'])

@qnaplcd.command()
def shutdown():
    "a short shutdown script to print a message on the LCD panel and terminate."
    lcd = QnapLCD()
    lcd.backlight(True)
    lcd.reset()
    lcd.clear()
    lcd.write(0, [platform.node(), 'Shutting Down...'])
