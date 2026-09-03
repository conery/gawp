#
# Define a Rich Console object and styles used in terminal output
#

import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style
from rich.table import Table, Column
from rich.theme import Theme

from .config import config

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

    t = Table(
        "Section",
        "Setting",
        "Value",
        title="Configuration",
        title_justify='left',
        title_style='table_header',
        show_header=False,
    )
    t.add_row("position", "sheet", config.position.sheet)
    t.add_row("", "category_col", config.position.category_col)
    t.add_row("", "cell_category", config.position.cell_category)
    t.add_row("", "measurement_category", config.position.measurement_category)

    t.add_section()
    t.add_row("position.cell", "id_col_1", config.position.cell.id_col_1)
    t.add_row("", "id_col_2", config.position.cell.id_col_2)
    t.add_row("", "x_coord", config.position.cell.x_coord)
    t.add_row("", "y_coord", config.position.cell.y_coord)

    t.add_section()
    t.add_row("position.measurement", "name_col", config.position.measurement.name_col)
    t.add_row("", "x_coord", config.position.measurement.x_coord)
    t.add_row("", "y_coord", config.position.measurement.y_coord)

    t.add_section()
    t.add_row("meioticstage", "id_col",  config.meioticstage.id_col)
    t.add_row("", "stage_names", str(config.meioticstage.stage_names))

    t.add_section()
    t.add_row("imaris", "data", config.imaris.data)
    t.add_row("", "measurements", config.imaris.measurements)

    t.add_section()
    t.add_row("output", "data", config.output.data)
    t.add_row("", "log", config.output.log)

    console.print()
    console.print(t)


