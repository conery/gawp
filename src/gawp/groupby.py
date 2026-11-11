#
# Plugin for groups
#

import logging
import tomllib

import pandas as pd

from .io import fetch_sheet
from .plugin import Plugin, plugins


class GroupSheet:

    fields = {
        'sheet': '',
        'column': '',
        'category_column': '',
        'category': '',
        'group': '',
        'aggregation_function': '',
        'aggregation_name': '',
        'index': '',
    }

    def __init__(self, toml=None, **kwargs):
        if toml:
            dct = tomllib.loads(toml)
            kwargs = dct['join']
        Plugin.__init__(self,GroupSheet.fields,kwargs)
        for field in ['sheet','column','group','aggregation_function','aggregation_name']:
            assert getattr(self,field), '[group] section is missing a {field} value'
        try:
            for field in ['category_column','category','index']:
                if getattr(self,field) == '':
                    setattr(self,field,getattr(plugins.geometry.foci,field))
                    logging.debug(f'group.{self.sheet}.{field} set to default: {getattr(self,field)}')
        except AttributeError as err:
            logging.error(f'Group plugin for "{self.sheet}" expecting {field} attribute from geometry.foci')
 

class Group(Plugin):

    def __init__(self, lst):
        '''
        Create a new Group plugin.
        '''
        super().__init__({},{})
        self.sheets = lst
        self.grouped_frame = None

    @staticmethod
    def defaults():
        return Plugin.defaults("group.x", GroupSheet.fields)

    def apply(self, xls):
        '''
        Create groups in each individual sheet, return them in a single frame.

        Argumnets:
            xls:  the spreadsheet file containing the sheets
        '''

        # Helper function, make a frame from the specified category
        def fetch_rows(category):
            return fetch_sheet(
                f = xls,
                name = obj.sheet,
                id_cols = obj.index,
                filter = [obj.category_column, category]
            )
        
        frames = []
        for obj in self.sheets:
            # fetch the rows that correspond to foci
            data_frame = fetch_rows(obj.category)

            # fetch the rows that will be grouped
            grp_frame = fetch_rows(obj.group)

            # make the groups
            agg = pd.NamedAgg(column=obj.column, aggfunc=obj.aggregation_function)
            grouped = grp_frame.groupby(obj.column).agg(**{obj.aggregation_name: agg})

            # join the groups with the data
            joined = data_frame.join(grouped, on=obj.column)

            # the frame to return is has the same index as the data and one column
            # with the aggregates
            frames.append(joined[[obj.aggregation_name]])
            
        self.grouped_frame = pd.concat(frames, axis=1)
        return self.grouped_frame
    