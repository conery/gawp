"""
Unit tests for gawp.config
"""

import pytest

from gawp.config import Config, initialize_config

TEST_CONFIG = 'tests/unit/fixtures/test_config.toml'

class TestConfig:

    def test_default_config(self):
        '''
        Check the default configuration settings
        '''
        initialize_config()
        assert Config.Position.sheet == 'Position'
        assert Config.Position.Cell.id_col_1 == 'Surpass Object'
        assert Config.Position.Cell.id_col_2 == 'ID'
        assert Config.Position.Cell.category == 'Category'
        assert Config.Position.Cell.x_coord == 'Position X'
        assert Config.Position.Cell.y_coord == 'Position Y'
        assert Config.Position.Measurement.name == 'Name'
        assert Config.Position.Measurement.category == 'Category'
        assert Config.Position.Measurement.x_coord == 'Position X'
        assert Config.Position.Measurement.y_coord == 'Position Y'

    def test_initialize_config(self):
        '''
        Test the function that loads settings from a TOML file
        '''
        initialize_config(TEST_CONFIG)
        # these items are changed in the config cile
        assert Config.Position.sheet == 'Pos'
        assert Config.Position.Cell.x_coord == 'X'
        assert Config.Position.Cell.y_coord == 'Y'
        assert Config.Position.Measurement.name == 'Z'
        # these items should be left unchanged and have the default values
        assert Config.Position.Cell.id_col_1 == 'Surpass Object'
        assert Config.Position.Cell.id_col_2 == 'ID'
        assert Config.Position.Cell.category == 'Category'
        assert Config.Position.Measurement.category == 'Category'
        assert Config.Position.Measurement.x_coord == 'Position X'
        assert Config.Position.Measurement.y_coord == 'Position Y'
