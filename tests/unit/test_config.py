"""
Unit tests for gawp.config
"""

import pytest

from gawp.config import config, initialize_config

TEST_CONFIG = 'tests/unit/fixtures/test_config.toml'

class TestConfig:

    def test_default_config(self):
        '''
        Check the default configuration settings in the global config
        '''
        assert config.position.sheet == 'Position'
        assert config.position.category_col == 'Category'
        assert config.position.cell_category == 'Surface'
        assert config.position.measurement_category == 'MeasurementPoint'
        assert config.position.cell.id_col_1 == 'Surpass Object'
        assert config.position.cell.id_col_2 == 'ID'
        assert config.position.cell.x_coord == 'Position X'
        assert config.position.cell.y_coord == 'Position Y'
        assert config.position.measurement.name_col == 'Name'
        assert config.position.measurement.x_coord == 'Position X'
        assert config.position.measurement.y_coord == 'Position Y'
        assert config.meioticstage.id_col == 'GonadID'
        assert config.meioticstage.stage_names == ['TZ_start','TZ_end','Pachy_end']
        assert config.imaris.data == ''
        assert config.imaris.measurements == ''
        assert config.output.data == ''
        assert config.output.log == ''

    def test_initialize_from_file(self):
        '''
        Test the function that loads settings from a TOML file
        '''
        initialize_config(fn=TEST_CONFIG)
        # these items are changed in the config cile
        assert config.position.sheet == 'Pos'
        assert config.position.cell.x_coord == 'X'
        assert config.position.cell.y_coord == 'Y'
        assert config.position.measurement.name_col == 'Z'
        assert config.imaris.data == './data/PRG*'
        assert config.output.data == '.'
        # these items should have the default values
        assert config.position.category_col == 'Category'
        assert config.position.cell_category == 'Surface'
        assert config.position.measurement_category == 'MeasurementPoint'
        assert config.position.cell.id_col_1 == 'Surpass Object'
        assert config.position.cell.id_col_2 == 'ID'
        assert config.position.measurement.x_coord == 'Position X'
        assert config.position.measurement.y_coord == 'Position Y'
        assert config.meioticstage.id_col == 'GonadID'
        assert config.meioticstage.stage_names == ['TZ_start','TZ_end','Pachy_end']
        assert config.imaris.measurements == ''
        assert config.output.log == ''

    def test_initialize_from_text(self):
        '''
        Test the function that loads settings from a text
        '''
        test_config = '''
            [position]
            sheet = 'Text'

            [position.cell]
            x_coord = 'P'
            y_coord = 'Q'

            [position.measurement]
            name_col = 'R'
        '''
        initialize_config(text=test_config)
        assert config.position.sheet == 'Text'
        assert config.position.cell.x_coord == 'P'
        assert config.position.cell.y_coord == 'Q'
        assert config.position.measurement.name_col == 'R'
        # these items should have the default values
        assert config.position.category_col == 'Category'
        assert config.position.cell_category == 'Surface'
        assert config.position.measurement_category == 'MeasurementPoint'
        assert config.position.cell.id_col_1 == 'Surpass Object'
        assert config.position.cell.id_col_2 == 'ID'
        assert config.position.measurement.x_coord == 'Position X'
        assert config.position.measurement.y_coord == 'Position Y'
        assert config.meioticstage.id_col == 'GonadID'
        assert config.meioticstage.stage_names == ['TZ_start','TZ_end','Pachy_end']
        assert config.imaris.data == ''
        assert config.imaris.measurements == ''
        assert config.output.data == ''
        assert config.output.log == ''

    @classmethod
    def teardown_class(cls):
        '''
        Function called after the last test, resets the global Config
        class for future tests.
        '''
        initialize_config()
        