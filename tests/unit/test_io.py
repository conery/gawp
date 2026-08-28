"""
Unit tests for gawp.io
"""

import pytest

import pandas as pd
import geopandas as gp
from gawp.io import parse_positions, get_cell_positions, get_measurements

TEST_DATA = 'data//PRG-1_herm_g05_sample.xlsx'

@pytest.fixture
def xls_file(scope='module'):
    return pd.ExcelFile(TEST_DATA, engine='calamine')

class TestIO:

    def test_open_xslx(self, xls_file):
        '''
        Make sure we can open the spreadsheet
        '''
        assert len(xls_file.sheet_names) == 39
        assert 'Position' in xls_file.sheet_names

    def test_parse_positions(self, xls_file):
        """
        Test the function that parses the Position sheet in the XLS file
        """
        sf = parse_positions(xls_file)
        assert len(sf) == 4596
        assert {'Position X', 'Position Y', 'Category'} < set(sf.columns)

    def test_cell_positions(self, xls_file):
        """
        Test the get_cell_positions function, which gets x and y coordinates
        of cells from the Position sheet and returns them in a GeoPandas frame
        """
        sf = parse_positions(xls_file)
        df = get_cell_positions(sf)
        assert type(df) == gp.geodataframe.GeoDataFrame
        assert len(df) == 4579
        assert list(df.columns) == ['id', 'point']
        assert df['id'][0] == 'prg1_dk0'
        assert round(df['point'][0].x,3) == 21.794 
        assert round(df['point'][0].y,3) == 138.72

    def test_measurement_positions(self, xls_file):
        """
        Test the get_measurements function, which gets x and y coordinates
        of measurement points and returns them in a GeoPandas frame
        """
        sf = parse_positions(xls_file)
        df = get_measurements(sf)
        assert type(df) == gp.geodataframe.GeoDataFrame
        assert len(df) == 17
        assert list(df.columns) == ['name', 'point']
        assert df['name'][0] == 'A'
        assert round(df['point'][0].x,3) == 38.501
        assert round(df['point'][0].y,3) == 141.542
