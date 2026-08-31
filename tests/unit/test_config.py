"""
Unit tests for gawp.config
"""

import pytest

from gawp.config import Config, initialize_config

TEST_CONFIG = 'tests/unit/fixtures/test_config.toml'
RESET_CONFIG = 'tests/unit/fixtures/reset_config.toml'

class TestConfig:

    def test_default_config(self):
        '''
        Check the default configuration settings
        '''
        initialize_config()
        print('config blank')
        assert Config.Position.sheet == 'Position'
        assert Config.Position.category_col == 'Category'
        assert Config.Position.cell_category == 'Surface'
        assert Config.Position.measurement_category == 'MeasurementPoint'
        assert Config.Position.Cell.id_col_1 == 'Surpass Object'
        assert Config.Position.Cell.id_col_2 == 'ID'
        assert Config.Position.Cell.x_coord == 'Position X'
        assert Config.Position.Cell.y_coord == 'Position Y'
        assert Config.Position.Measurement.name_col == 'Name'
        assert Config.Position.Measurement.x_coord == 'Position X'
        assert Config.Position.Measurement.y_coord == 'Position Y'

    def test_initialize_config(self):
        '''
        Test the function that loads settings from a TOML file
        '''
        initialize_config(TEST_CONFIG)
        print(TEST_CONFIG)
        # these items are changed in the config cile
        assert Config.Position.sheet == 'Pos'
        assert Config.Position.Cell.x_coord == 'X'
        assert Config.Position.Cell.y_coord == 'Y'
        assert Config.Position.Measurement.name_col == 'Z'
        # these items should be left unchanged and have the default values
        assert Config.Position.category_col == 'Category'
        assert Config.Position.cell_category == 'Surface'
        assert Config.Position.measurement_category == 'MeasurementPoint'
        assert Config.Position.Cell.id_col_1 == 'Surpass Object'
        assert Config.Position.Cell.id_col_2 == 'ID'
        assert Config.Position.Measurement.x_coord == 'Position X'
        assert Config.Position.Measurement.y_coord == 'Position Y'

    @classmethod
    def teardown_class(cls):
        '''
        Function called after the last test, resets the global Config
        class for future tests.
        '''
        print('tearing down...')
        initialize_config(RESET_CONFIG)
