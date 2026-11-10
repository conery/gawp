"""
Unit tests for gawp.config
"""

import pytest

from gawp.config import initialize_config
from gawp.plugin import plugins

class TestConfig:

    def test_default(self):
        '''
        With an empty spec no plugins are installed
        '''
        initialize_config(text='')
        assert plugins.io is None
        assert plugins.io is None
        assert plugins.stages is None
        assert plugins.geometry is None
        assert plugins.join is None
        assert plugins.group is None

    def test_default_io(self):
        '''
        Check the default configuration settings of the IO plugin
        '''
        CONFIG = '''
        [io]
        '''
        initialize_config(text=CONFIG)
        assert plugins.io.spreadsheets == ''        
        assert plugins.io.output_dir == ''        
        assert plugins.io.output_name == ''        
        assert plugins.io.log == ''        

    def test_io(self):
        '''
        Check IO settings with specified values
        '''
        CONFIG = '''
        [io]
        spreadsheets = '*.xlsx'
        output_dir = 'dir'
        output_name = 'name'
        log = 'logarithm'
        '''
        initialize_config(text=CONFIG)
        assert plugins.io.spreadsheets == '*.xlsx'        
        assert plugins.io.output_dir == 'dir'        
        assert plugins.io.output_name == 'name'        
        assert plugins.io.log == 'logarithm'        

    def test_minimal_geometry(self):
        '''
        If a configuration has a geometry section it also needs a foci subsection.
        '''
        CONFIG = '''
        [geometry]
        '''
        with pytest.raises(ValueError):
            initialize_config(text=CONFIG)

    def test_geometry(self):
        '''
        A geometry section can leave out a measurements section
        '''
        CONFIG = '''
        [geometry]
        [geometry.foci]
        '''
        initialize_config(text=CONFIG)
        assert plugins.geometry.measurements is None

    def test_default_foci(self):
        '''
        Check the default configuration of the Foci plugin.
        '''
        CONFIG = '''
        [geometry]
        [geometry.foci]
        '''
        initialize_config(text=CONFIG)
        assert plugins.geometry.foci.sheet_name == 'Position'
        assert plugins.geometry.foci.category_column == 'Category'
        assert plugins.geometry.foci.x_coord == 'Position X'
        assert plugins.geometry.foci.y_coord == 'Position Y'
        assert plugins.geometry.foci.category == 'Surface'
        assert plugins.geometry.foci.index == ['Surpass Object','ID']


    def test_foci(self):
        '''
        Check the configuration of Foci with specified settings
        '''
        CONFIG = '''
        [geometry]
        sheet_name = 'Geo'
        category_column = 'Cat'
        x_coord = 'X'
        y_coord = 'Y'

        [geometry.foci]
        category = 'Surf'
        index = 'ID'
        '''
        initialize_config(text=CONFIG)
        assert plugins.geometry.foci.sheet_name == 'Geo'
        assert plugins.geometry.foci.category_column == 'Cat'
        assert plugins.geometry.foci.x_coord == 'X'
        assert plugins.geometry.foci.y_coord == 'Y'
        assert plugins.geometry.foci.category == 'Surf'
        assert plugins.geometry.foci.index == 'ID'

    def test_default_measurements(self):
        '''
        Check the default configuration of the Measurements plugin
        '''
        CONFIG = '''
        [geometry]
        [geometry.foci]
        [geometry.measurements]
        '''
        initialize_config(text=CONFIG)
        assert plugins.geometry.measurements.sheet_name == 'Position'
        assert plugins.geometry.measurements.category_column == 'Category'
        assert plugins.geometry.measurements.x_coord == 'Position X'
        assert plugins.geometry.measurements.y_coord == 'Position Y'
        assert plugins.geometry.measurements.category == 'MeasurementPoint'
        assert plugins.geometry.measurements.index == 'Name'

    def test_measurements(self):
        '''
        Check the configuration of Measurements with specified settings
        '''
        CONFIG = '''
        [geometry]
        sheet_name = 'Geo'
        category_column = 'Cat'
        x_coord = 'X'
        y_coord = 'Y'

        [geometry.foci]

        [geometry.measurements]
        category = 'Point'
        index = 'ID'
        '''
        initialize_config(text=CONFIG)
        assert plugins.geometry.measurements.sheet_name == 'Geo'
        assert plugins.geometry.measurements.category_column == 'Cat'
        assert plugins.geometry.measurements.x_coord == 'X'
        assert plugins.geometry.measurements.y_coord == 'Y'
        assert plugins.geometry.measurements.category == 'Point'
        assert plugins.geometry.measurements.index == 'ID'

    def test_empty_join(self):
        '''
        An empty join section will parse but raise an error at runtime saying
        there are no sheets to join
        '''
        CONFIG = '''
        [join]
        '''
        initialize_config(text=CONFIG)
        assert plugins.join.sheets == []       

    def test_join(self):
        '''
        Check join settings with specified values
        '''
        CONFIG = '''
        [join.volume]
        sheet = 'Volume'
        column = 'Volume'
        index = ['Surpass Object','ID']

        [join.sphericity]
        sheet = 'Sphericity'
        column = 'Sphericity'
        index = ['Surpass Object','ID']
        '''
        initialize_config(text=CONFIG)
        assert len(plugins.join.sheets) == 2
        assert plugins.join.sheets[0].sheet == 'Volume'
        assert plugins.join.sheets[0].column == 'Volume'
        assert plugins.join.sheets[1].sheet == 'Sphericity'
        assert plugins.join.sheets[1].column == 'Sphericity'

    def test_default_stages(self):
        '''
        Check the default configuration of the Stages plugin.  The file option
        is required, others are optional.
        '''
        CONFIG = '''
        [stages]
        file = 'foo'
        '''
        initialize_config(text=CONFIG)
        assert plugins.stages.file == 'foo'
        assert plugins.stages.index == 'GonadID'
        assert plugins.stages.filter_column == 'Stitched?'
        assert plugins.stages.filter == 'TRUE'
        assert plugins.stages.stage_columns == ['TZ_start','TZ_end','Pachy_end']
        assert plugins.stages.stage_names == ['PMT', 'TZ', 'PACH']

    def test_stages(self):
        '''
        Check the configuration of Stages with specified settings
        '''
        CONFIG = '''
        [stages]
        file = 'foo.xlsx'
        index = 'ID'
        filter_column = 'yes'
        filter = 'true'
        stage_columns = ['a']
        stage_names = ['A']
        '''
        initialize_config(text=CONFIG)
        assert plugins.stages.file == 'foo.xlsx'
        assert plugins.stages.index == 'ID'
        assert plugins.stages.filter_column == 'yes'
        assert plugins.stages.filter == 'true'
        assert plugins.stages.stage_columns == ['a']
        assert plugins.stages.stage_names == ['A']
