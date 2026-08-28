"""
gawp.io

Functions for reading and writing spreadsheet files
"""

import geopandas as gp
import pandas as pd
from shapely.geometry import Point

# TODO  define column names in config file

def parse_positions(f:pd.ExcelFile, sheet_name:str="Position"):
    '''
    Read location data from an XLS file exported by Imaris.  Returns a Pandas
    data frame with all the rows from the sheet that has positions.  By default
    the name of that sheet is "Position" but another name can be passed.

    TODO:  get the sheet name and column names from a config file
     
    Arguments:
        f:  the XLS file to read from
        sheet_name (optional): the name of the sheet that has the data (default: "Position")

    Returns:
        a Pandas frame containing the ID, X and Y location, and category from each row
    '''
    assert sheet_name in f.sheet_names, f"spreadheet is missing the '{sheet_name}' sheet"
    sf = f.parse(sheet_name, header=1)

    required_cols = ['ID', 'Name', 'Category', 'Surpass Object', 'Position X', 'Position Y']
    assert set(required_cols) < set(sf.columns), f"sheet is missing one or more required colums ({required_cols})"

    return sf[required_cols]

def get_cell_positions(df: pd.DataFrame, category:str="Surface"):
    '''
    Extract the cell location data from a DataFrame created from the Position sheet in 
    an XLS file exported by Imaris.  
     
    Arguments:
        df:  the data frame with position data
        category (optional): the type of data to read (default: "Surface")

    Returns:
        a GeoDataFrame containing unique IDs for each cell and a Point object with the
        x and y coordinates of the cell.
    '''
    pf = df[df['Category']==category]
    pf.index = range(len(pf))

    return gp.GeoDataFrame({
        'id': pf['Surpass Object'] + pf['ID'].apply(str),
        'point': [Point(pf.loc[i]['Position X'], pf.loc[i]['Position Y']) for i in range(len(pf))]
    }).set_geometry('point')

def get_measurements(df: pd.DataFrame, category:str="MeasurementPoint"):
    '''
    Extract the measurement locations from a DataFrame created from the Position sheet in 
    an XLS file exported by Imaris.
     
    Arguments:
        df:  the data frame with position data
        category (optional): the type of data to read (default: "MeasurementPoint")

    Returns:
        a GeoDataFrame containing unique IDs for each measurement ppint and a Point object with the
        x and y coordinates of the measurement.
    '''
    pf = df[df['Category']==category]
    pf.index = range(len(pf))

    return gp.GeoDataFrame({
        'name': pf['Name'],
        'point': [Point(pf.loc[i]['Position X'], pf.loc[i]['Position Y']) for i in range(len(pf))]
    }).set_geometry('point')

