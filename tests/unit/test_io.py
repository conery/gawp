"""
Unit tests for gawp.io
"""

import pytest

import pandas as pd
import geopandas as gp
from gawp.io import read_cell_positions

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

    def test_parse_position_sheet(self, xls_file):
        """
        Parse the Position sheet in the XLS file
        """
        sheet = xls_file.parse('Position', header=1)
        assert len(sheet) == 4596
        assert {'Position X', 'Position Y', 'Category'} < set(sheet.columns)

    def test_read_cell_positions(self, xls_file):
        """
        Test the read_cell_positions function, which gets x and y coordinates
        of cells from the Position sheet and returns them in a GeoPandas frame
        """
        df = read_cell_positions(xls_file)
        assert type(df) == gp.geodataframe.GeoDataFrame
        assert len(df) == 4579
        assert list(df.columns) == ['id', 'point']
        assert df.loc[0].id == 'prg1_dk0'
        assert round(df.loc[0].point.x,3) == 21.794 
        assert round(df.loc[0].point.y,3) == 138.72
