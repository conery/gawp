#
# Define a Rich Console object and styles used in terminal output
#

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style
from rich.table import Table, Column
from rich.theme import Theme

# from .config import config

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

# console = Console(theme=dark_terminal, emoji=None)
console = Console(theme=light_terminal)

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

def print_config():
    '''
    Print a table showing configuration settings.
    '''

    console.print('[bold red]Broken -- needs to get settings from plugins')
    return

    t = Table(
        "Section",
        "Setting",
        "Value",
        title="Configuration",
        title_justify='left',
        title_style='table_header',
        show_header=False,
    )
    t.add_row("io", "spreadsheets", config.io.spreadsheets)
    t.add_row("", "output_dir", config.io.output_dir)
    t.add_row("", "output_name", config.io.output_name)
    t.add_row("", "log", config.io.log)

    t.add_section()
    t.add_row("geometry", "sheet_name", config.geometry.sheet_name)
    t.add_row("", "category_column", config.geometry.category_column)
    t.add_row("", "x_coord", config.geometry.x_coord)
    t.add_row("", "y_coord", config.geometry.y_coord)

    t.add_section()
    t.add_row("geometry.foci", "category", config.geometry.foci.category)
    t.add_row("", "index", str(config.geometry.foci.index))

    t.add_section()
    t.add_row("geometry.measurement", "category", config.geometry.measurement.category)
    t.add_row("", "index", str(config.geometry.measurement.index))

    t.add_section()
    t.add_row("meiotic_stages", "file",  config.meiotic_stages.file)
    t.add_row("", "index", config.meiotic_stages.index)
    t.add_row("", "stage_names", str(config.meiotic_stages.stage_names))

    console.print()
    console.print(t)


