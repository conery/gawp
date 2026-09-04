"""
gawp.io

Functions for reading and writing spreadsheet files
"""

import logging
from pathlib import Path

import geopandas as gp
import pandas as pd
from shapely.geometry import Point

from .config import config, settings

##########################
#
# make_output_dir
#

def make_output_dir(args):
    '''
    Return the path to the directory where outputs will be written.  A name
    specified on the command line takes precedence over a name in the config
    file.  Creates the directory if it does not exist.

    Arguments:
        args:  command line arguments

    Returns:
        the name of the output directory
    '''
    fn = args.output or config.output.data
    if not fn:
        raise ValueError('specify an output directory in the config file or with --output')

    p = Path(fn).resolve()
    try:
        p.mkdir(parents=True, exist_ok=True)
    except FileExistsError as err:
        logging.error(f"can't use {fn} for directory name; there is an existing file named {p}")
        raise ValueError("choose a different output name or rename/delete the existing file")

    logging.info(f'output directory: {p}')
    return p

##########################
#
# read_stages
#

def read_stages():
    """
    The IDs of the measurements that mark the starts of meiotic stages are all
    in a single spreadsheet.  Parse that spreadsheet and return it as a
    Pandas DataFrame.

    Note: the data set names in the ID column from the spreadsheet are file names.
    The index in the new data frame is created by stripping the extension from the
    file names.

    Arguments:
        none

    Returns:
        a data frame with stage data
    """
    if fn := config.imaris.measurements:
        p = Path(fn).resolve()
        if not p.is_file():
            logging.warn(f'imaris.measurements "{fn}": file not found')
            res = None
        else:
            ID_COL = config.meioticstage.id_col
            with pd.ExcelFile(p, engine='calamine') as f:
                df = f.parse()
                df[ID_COL] = df[ID_COL].str.split('.').str[:-1].str.join('.')
                res = df.set_index(ID_COL)
    else:
        logging.warn(f'config has no value for imaris.measurement')
        res = None

    if res is None:
        logging.warn('meiotic stages will not be assigned')
    else:
        logging.debug(f'using meioitic stage names from {p}')

    return res

##########################
#
# get_spreadsheet_names
#

def get_spreadsheet_names(args):
    '''
    Return a list of names of spreasheets with Imaris data.

    File names from the command line take precedence over names from the 
    config file.  Warns the user if a file does not exist.

    Arguments:
        args:  command line arguments

    Returns:
        a list of paths to spreadsheeets
    '''
    if args.file:
        globbed = [f.resolve() for f in args.file]
    elif config.imaris.data:
        globbed = [f.resolve() for p in config.imaris.data.split() for f in Path('.').glob(p)]
        if len(globbed) == 0:
            raise ValueError(f'no files match pattern from imaris.data: "{config.imaris.data}"')
    else:
        raise ValueError('Specify path to input data in configuration or with --file')

    res = []
    for fn in globbed:
        if Path.is_dir(fn):
            logging.warn(f'ignoring directory name {fn}; use {fn}/* to specify all files in a directory')
            continue
        if not Path.exists(fn):
            logging.warn(f'file not found: {fn}')
            continue
        res.append(fn)

    return res

##########################
#
# read_positions
#

def read_positions(fn):
    '''
    Read location data from an XLS file exported by Imaris.  Returns a Pandas
    data frame with all the rows from the sheet that has positions.  
     
    Arguments:
        fn:  the name of the XLS file to read from

    Returns:
        a Pandas frame containing the ID, X and Y location, and category from each row
    '''

    sheet_name = config.position.sheet

    with pd.ExcelFile(fn, engine="calamine") as f:
        assert sheet_name in f.sheet_names, f"spreadheet is missing the '{sheet_name}' sheet"
        sf = f.parse(sheet_name, header=1)

    required_cols = { config.position.category_col }
    required_cols |= set(settings(config.position.cell).values())
    required_cols |= set(settings(config.position.measurement).values())
    assert required_cols < set(sf.columns), f'sheet "{sheet_name}" is missing one or more required colums ({required_cols})'

    return sf[list(required_cols)]

##########################
#
# get_cell_positions
#

def get_cell_positions(df: pd.DataFrame):
    '''
    Extract the cell location data from a DataFrame created from the Position sheet in 
    an XLS file exported by Imaris.  
     
    Arguments:
        df:  the data frame with position data

    Returns:
        a GeoDataFrame containing unique IDs for each cell and a Point object with the
        x and y coordinates of the cell.
    '''
    CATEGORY_COL = config.position.category_col
    CATEGORY_VAL = config.position.cell_category
    ID_PART_1 = config.position.cell.id_col_1
    ID_PART_2 = config.position.cell.id_col_2
    X_COORD = config.position.cell.x_coord
    Y_COORD = config.position.cell.y_coord

    pf = df[df[CATEGORY_COL]==CATEGORY_VAL]
    pf.index = range(len(pf))

    return gp.GeoDataFrame({
        'id': pf[ID_PART_1] + pf[ID_PART_2].apply(str),
        'point': [Point(pf.loc[i][X_COORD], pf.loc[i][Y_COORD]) for i in range(len(pf))]
    }).set_geometry('point')

##########################
#
# get_measurement_positions
#

def get_measurement_positions(df: pd.DataFrame):
    '''
    Extract the measurement locations from a DataFrame created from the Position sheet in 
    an XLS file exported by Imaris.
     
    Arguments:
        df:  the data frame with position data

    Returns:
        a GeoDataFrame containing unique IDs for each measurement ppint and a Point object with the
        x and y coordinates of the measurement.
    '''
    CATEGORY_COL = config.position.category_col
    CATEGORY_VAL = config.position.measurement_category
    ID_COL = config.position.measurement.name_col
    X_COORD = config.position.measurement.x_coord
    Y_COORD = config.position.measurement.y_coord

    pf = df[df[CATEGORY_COL]==CATEGORY_VAL]
    pf.index = range(len(pf))

    return gp.GeoDataFrame({
        'name': pf[ID_COL],
        'point': [Point(pf.loc[i][X_COORD], pf.loc[i][Y_COORD]) for i in range(len(pf))]
    }).set_geometry('point')

