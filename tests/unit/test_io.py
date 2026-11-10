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
    return io.open_spreadsheet(TEST_DATA)

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
        Parse the Positions sheet, return a frame with no index and all rows.
        """
        sf = io.fetch_sheet(data_file, name='Position')
        assert len(sf) == 4596
        assert type(sf.index) == pd.RangeIndex
        assert {'Position X', 'Position Y', 'Category'} < set(sf.columns)
        
    def test_read_indexed_positions(self, data_file):
        """
        Parse the Positions sheet, use one of the columns as the index.  The index
        is not unique, so fetching an item by index will return several rows.
        """
        sf = io.fetch_sheet(data_file, name='Position', id_cols=['Surpass Object'])
        assert type(sf.index) == pd.Index
        assert 'prg1_dk' in sf.index
        assert len(sf.loc['prg1_dk']) == 622

    def test_read_unique_indexed_positions(self, data_file):
        """
        Parse the Positions sheet, use two columns as the index, each row will
        now have a unique ID
        """
        sf = io.fetch_sheet(data_file, name='Position', id_cols=['Surpass Object','ID'])
        assert type(sf.index) == pd.Index
        assert 'prg1_dk.1' in sf.index

    def test_read_foci_positions(self, data_file):
        """
        The foci in the test data are in rows where the Category column is "Surface"
        """
        df = io.fetch_sheet(
            data_file, 
            name='Position', 
            id_cols=['Surpass Object','ID'],
            filter=['Category','Surface'])
        assert len(df) == 4579

    def test_measurement_positions(self, data_file):
        """
        The measurements in the test data are in rows where the Category column is "MeasurementPoint"

        """
        df = io.fetch_sheet(
            data_file, 
            name='Position', 
            id_cols=['Name'],
            filter=['Category','MeasurementPoint'])
        assert len(df) == 17

