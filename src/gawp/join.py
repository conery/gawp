#
# Plugin for joins
#

import logging
import tomllib

import pandas as pd

from .io import fetch_sheet
from .plugin import Plugin


class Sheet:

    fields = {
        'sheet': '',
        'column': '',
        'index': ['Surpass Object','ID'],
    }

    def __init__(self, toml=None, **kwargs):
        if toml:
            dct = tomllib.loads(toml)
            kwargs = dct['join']
        Plugin.__init__(self,Sheet.fields,kwargs)
        assert self.sheet, '[join] section is missing the sheet name'
        assert self.column, '[join] section is missing the column name'

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
    