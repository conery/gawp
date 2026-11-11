#
# Plugin for joins
#

import logging
import tomllib

import pandas as pd

from .io import fetch_sheet
from .plugin import Plugin, plugins


class Sheet:

    fields = {
        'sheet': '',
        'column': '',
        'category_column': '',
        'category': '',
        'index': '',
    }

    def __init__(self, toml=None, **kwargs):
        if toml:
            dct = tomllib.loads(toml)
            kwargs = dct['join']
        Plugin.__init__(self,Sheet.fields,kwargs)
        assert self.sheet, '[join] section is missing the sheet name'
        assert self.column, '[join] section is missing the column name'
        try:
            for field in ['category_column','category','index']:
                if getattr(self,field) == '':
                    setattr(self,field,getattr(plugins.geometry.foci,field))
                    logging.debug(f'join.{self.sheet}.{field} set to default: {getattr(self,field)}')
        except AttributeError as err:
            logging.error(f'Join plugin for "{self.sheet}" expecting {field} attribute from geometry.foci')
 

class Join(Plugin):

    def __init__(self, lst):
        '''
        Create a new Join plugin that will add sheets to a position frame.
        '''
        super().__init__({},{})
        self.sheets = lst

    @staticmethod
    def defaults():
        return Plugin.defaults("join.x", Sheet.fields)

    def apply(self, xls):
        '''
        Parse each of the sheets, extract the data columns, return them in a
        single frame.

        Argumnets:
            xls:  the spreadsheet file containing the sheets
        '''
        frames = []
        for obj in self.sheets:
            df = fetch_sheet(
                f = xls,
                name = obj.sheet,
                id_cols = obj.index,
            )
            frames.append(df[obj.column])
            logging.debug(f'  join: added {obj.sheet}')

        self.combined_frame = pd.concat(frames, axis=1)
        return self.combined_frame
    