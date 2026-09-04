"""
Unit tests for gawp.io
"""

import pytest

import pandas as pd
import geopandas as gp
import gawp.io as io

TEST_DATA = 'data/PRG-1_herm_g05_sample.xlsx'
TEST_STAGES = 'data/stages.xlsx'

@pytest.fixture
def data_file(scope='module'):
    return pd.ExcelFile(TEST_DATA, engine='calamine')

@pytest.fixture
def stage_file(scope='module'):
    return pd.ExcelFile(TEST_STAGES, engine='calamine')

class TestIO:

    def test_open_xslx(self, data_file):
        '''
        Make sure we can open the spreadsheet
        '''
        assert len(data_file.sheet_names) == 39
        assert 'Position' in data_file.sheet_names

    def test_read_positions(self, data_file):
        """
        Test the function that parses the Position sheet in the XLS file
        """
        sf = io.read_positions(TEST_DATA)
        assert len(sf) == 4596
        assert {'Position X', 'Position Y', 'Category'} < set(sf.columns)

    def test_cell_positions(self, data_file):
        """
        Test the get_cell_positions function, which gets x and y coordinates
        of cells from the Position sheet and returns them in a GeoPandas frame
        """
        sf = io.read_positions(TEST_DATA)
        df = io.get_cell_positions(sf)
        assert type(df) == gp.geodataframe.GeoDataFrame
        assert len(df) == 4579
        assert list(df.columns) == ['id', 'point']
        assert df['id'][0] == 'prg1_dk0'
        assert round(df['point'][0].x,3) == 21.794 
        assert round(df['point'][0].y,3) == 138.72

    def test_measurement_positions(self, data_file):
        """
        Test the get_measurements function, which gets x and y coordinates
        of measurement points and returns them in a GeoPandas frame
        """
        sf = io.read_positions(TEST_DATA)
        df = io.get_measurement_positions(sf)
        assert type(df) == gp.geodataframe.GeoDataFrame
        assert len(df) == 17
        assert list(df.columns) == ['name', 'point']
        assert df['name'][0] == 'A'
        assert round(df['point'][0].x,3) == 38.501
        assert round(df['point'][0].y,3) == 141.542

    def test_read_stages(self, stage_file):
        """
        Test the function that reads the stage data for the test data set
        """
        df = io.read_stages(TEST_STAGES)
        row = df.loc['210924_DLW67_noAUX_HS_RAD51_AID_herm_g05_stitched']
        assert row['TZ_start'] == 'G'
        assert row['TZ_end'] == 'L'
        assert row['Pachy_end'] == 'Q'
    