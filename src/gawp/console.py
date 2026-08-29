#
# Define a Rich Console object and styles used in terminal output
#

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style
from rich.table import Table, Column as TableColumn
from rich.theme import Theme

# Suggested colors for terminals with a light theme

light_terminal = Theme({
    'table_header': Style(
        color = 'black',
        bgcolor= 'grey82',
    ),
})

# Suggest colors for terminals with a dark theme

dark_terminal = Theme({
    'table_header': Style(
        color = 'white',
        bgcolor= 'dodger_blue2',
    ),
    'highlight': Style(
        color = 'honeydew2',
        bgcolor = 'grey42',
    ),
    'error': Style(
        color = 'red'
    ),
    'autofill': Style(
        color = 'honeydew2',
    ),
    'editable': Style(
        color = 'white',
        bgcolor = 'grey39',
        italic = True
    ),
    'edited': Style(
        color = 'dodger_blue2',
        bgcolor = 'grey82',
    ),
})

console = Console(theme=dark_terminal, emoji=None)
# console = Console(theme=light_terminal)

def setup_logging(arg):
    """
    Configure the logging module.
    """
    match arg:
        case 'info':
            level = logging.INFO
        case 'debug':
            level = logging.DEBUG
        case _:
            level = logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(message)s',
        handlers = [RichHandler(markup=True, rich_tracebacks=True, show_time=False, show_path=(arg=='debug'))],
    )


