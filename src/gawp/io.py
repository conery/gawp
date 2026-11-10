#
#
# Plugin and utility functions for reading and writing spreadsheet files
#

import logging
from pathlib import Path
import importlib.resources
import tomllib

import geopandas as gp
import pandas as pd
from shapely.geometry import Point

from .plugin import Plugin

class IO(Plugin):

    fields = {
        'spreadsheets': '',
        'output_dir': '',
        'output_name': '',
        'log': '',
    }

    def __init__(self, toml=None, **kwargs):
        if toml:
            dct = tomllib.loads(toml)
            kwargs = dct['io']
        super().__init__(IO.fields,kwargs)
        self.resolved_output_path = None

    @staticmethod
    def defaults():
        return Plugin.defaults("io", IO.fields)

    def get_spreadsheet_names(self, args=None):
        '''
        Return a list of names of spreasheets with Imaris data.

        File names from the command line take precedence over names from the 
        config file.  Warns the user if a file does not exist.

        Arguments:
            args:  command line arguments

        Returns:
            a list of paths to spreadsheeets
        '''
        if args and args.file:
            globbed = [f.resolve() for f in args.file]
        elif self.spreadsheets:
            globbed = [f.resolve() for p in self.spreadsheets.split() for f in Path('.').glob(p)]
            if len(globbed) == 0:
                raise ValueError(f'no files match pattern from config: "{self.spreadsheets}"')
        else:
            raise ValueError('Specify path to input data in configuration or with --file')

        res = []
        for fn in globbed:
            if fn.name.startswith('~'):
                continue                    # ignore Excel temp files 🙄
            if Path.is_dir(fn):
                logging.warn(f'ignoring directory name {fn}; use {fn}/* to specify all files in a directory')
                continue
            if not Path.exists(fn):
                logging.warn(f'file not found: {fn}')
                continue
            res.append(fn)

        return res

    def make_output_dir(self, args=None):
        '''
        Return the path to the directory where outputs will be written.  A name
        specified on the command line takes precedence over a name in the config
        file.  Creates the directory if it does not exist.

        Arguments:
            args:  command line arguments

        Returns:
            the name of the output directory
        '''

        fn = (args and args.output) or self.output_dir
        if not fn:
            raise ValueError('specify an output directory in the config file or with --output')

        p = Path(fn).resolve()
        try:
            p.mkdir(parents=True, exist_ok=args.force)
        except FileExistsError as err:
            logging.error(f"Output folder {p} conflicts with existing folder.")
            raise ValueError("Choose a different output name or rename/delete the existing folder.")

        self.resolved_output_path = p
        logging.info(f'output directory: {p}')
        return p

    def make_output_path(self, fn):
        '''
        Create the path to an output file using the output directory and name pattern from 
        the config file.  Makes sure the file name ends with '.csv'.

        Arguments:
            fn: the name of spreadsheet that had the input data
        '''
        if self.resolved_output_path is None:
            raise ValueError(f'app did not call make_output_dir')
        p = self.output_name.format(fn=fn)
        return (self.resolved_output_path / p).with_suffix('.csv')

##########################
#
# Utility functions, called by apps or other plugins
#

#
# Return the path to one of the resources in the project directory.
#

def path_to_resource(s: str) -> Path:
    '''
    Return the path to a project resource.  Options are "notebooks" or
    "data", im which case the return value is the path to the directory
    containing the resources, or "gawp.toml", which returns the path to
    the default config file.

    Arguments:
        s: the type of resource

    Returns:
        the path to the resource    
    '''
    source_dir = importlib.resources.files("gawp")
    if s in {'data','notebooks'}:
        p = source_dir.parent.parent / s
    elif s == 'gawp.toml':
        logging.error('TBD: print default config')
        p = None
    else:
        p = None
    return p

#
# Open a spreadsheet file
#

def open_spreadsheet(fn: Path) -> pd.ExcelFile:
    '''
    Open an XLS or XLSX spreadsheet, return the file object.

    Arguments:
        fn: the file name

    Returns:
        an open ExcelFile object
    '''
    return pd.ExcelFile(fn, engine='calamine')

#
# Convert a sheet from an XLS file to a DataFrame
#

def fetch_sheet(f: pd.ExcelFile, name: str, id_cols = [], filter = []) -> pd.DataFrame:
    '''
    Extract a sheet from a spreadsheet, convert it to a DataFrame.  If a 
    list of column names is supplied create an index using values from
    those columns (the columns remain in the frame).

    Arguments:
        f: the Excel file that contains the sheet
        name:  the name of the sheet
        id_cols:  the namess of columns to use for the frame index

    Returns:
        a DataFrame with all the rows and columns from the sheet
    '''
    df = f.parse(name, header=1)

    required_cols = set(id_cols)
    if filter:
        required_cols.add(filter[0])
    assert required_cols < set(df.columns), f'sheet "{name}" is missing one or more required colums ({required_cols})'

    if filter:
        df = df[df[filter[0]] == filter[1]]
    
    if id_cols:
        ids = df[id_cols[0]].apply(str)
        ids.name = ''
        for col in id_cols[1:]:
            s = df[col].apply(str)
            ids += '.' + s
        df.index = ids

    return df
