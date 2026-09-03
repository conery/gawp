"""
gawp.io

Functions for reading and writing spreadsheet files
"""

import logging

import geopandas as gp
import pandas as pd
from shapely.geometry import Point

from .config import config, settings

def parse_positions(f:pd.ExcelFile):
    '''
    Read location data from an XLS file exported by Imaris.  Returns a Pandas
    data frame with all the rows from the sheet that has positions.  
     
    Arguments:
        f:  the XLS file to read from

    Returns:
        a Pandas frame containing the ID, X and Y location, and category from each row
    '''
    sheet_name = config.position.sheet
    assert sheet_name in f.sheet_names, f"spreadheet is missing the '{sheet_name}' sheet"
    sf = f.parse(sheet_name, header=1)

    required_cols = { config.position.category_col }
    required_cols |= set(settings(config.position.cell).values())
    required_cols |= set(settings(config.position.measurement).values())
    logging.debug(f'requred cols {required_cols}')
    assert required_cols < set(sf.columns), f'sheet "{sheet_name}" is missing one or more required colums ({required_cols})'

    return sf[list(required_cols)]

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

def read_stages(f:pd.ExcelFile):
    """
    The IDs of the measurements that mark the starts of meiotic stages are all
    in a single spreadsheet.  Parse that spreadsheet and return it as a
    Pandas DataFrame.

    Note: the data set names in the ID column from the spreadsheet are file names.
    The index in the new data frame is created by stripping the extension from the
    file names.

    Arguments:
        f: the XLS file containing meiotic stage data

    Returns:
        a data frame with stage data
    """
    ID_COL = config.meioticstage.id_col
    df = f.parse()
    df[ID_COL] = df[ID_COL].str.split('.').str[:-1].str.join('.')
    return df.set_index(ID_COL)
