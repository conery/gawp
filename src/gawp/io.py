"""
gawp.io

Functions for reading and writing spreadsheet files
"""

import geopandas as gp
import pandas as pd
from shapely.geometry import Point

# TODO  define column names in config file

def read_cell_positions(f:pd.ExcelFile, sheet:str="Position", category:str="Surface"):
    '''
    Read cell location data from an XLS file exported by Imaris.  Returns a Pandas
    data frame with the locations of all the rows in the specified category.
     
    Raises an exception if the file does not have a sheet named "Position" or if that
    sheet does not have the columns we need.

    Arguments:
        f:  the file to read from
        sheet (optional): the name of the sheet that has the data (default: "Position")
        category (optional): the type of data to read (default: "Surface")

    Returns:
        a Pandas frame containing unique IDs for each cell and a Point object with the
        x and y coordinates of the cell.
    '''
    assert "Position" in f.sheet_names, "spreadheet is missing the 'Position' sheet"
    sheet = f.parse("Position", header=1)

    for col in ['Category', 'Surpass Object', 'ID', 'Position X', 'Position Y']:
        assert col in sheet, f"sheet does not have a {col} column"

    pf = sheet[sheet['Category']==category]
    pf.index = range(len(pf))

    return gp.GeoDataFrame({
        'id': pf['Surpass Object'] + pf['ID'].apply(str),
        'point': [Point(pf.loc[i]['Position X'], pf.loc[i]['Position Y']) for i in range(len(pf))]
    }).set_geometry('point')
