#
# Plugin for meiotic stage data
#

import logging
from pathlib import Path
import tomllib

import numpy as np
import pandas as pd

from .plugin import Plugin

class Stages(Plugin):

    fields = {
        'file': '',
        'index': 'GonadID',
        'filter_column': 'Stitched?',
        'filter': 'TRUE',
        'stage_columns': ['TZ_start','TZ_end','Pachy_end'],
        'stage_names': ['PMT', 'TZ', 'PACH']
    }

    def __init__(self, toml=None, **kwargs):
        if toml:
            dct = tomllib.loads(toml)
            kwargs = dct['stages']
        super().__init__(Stages.fields,kwargs)
        assert self.file, '[stages] section of configuration is missing the file name'
        self.stage_frame = None

    @staticmethod
    def defaults():
        return Plugin.defaults("stages", Stages.fields)    

    def read_stage_boundaries(self):
        """
        The IDs of the measurements that mark the starts of meiotic stages are all
        in a single spreadsheet.  Parse that spreadsheet and save it as a
        Pandas DataFrame.

        Returns:
            a data frame with stage data
        """
        p = Path(self.file).resolve()
        if not p.is_file():
            raise ValueError(f'stages.file "{p}": file not found')

        ID_COL = self.index
        with pd.ExcelFile(p, engine='calamine') as f:
            df = f.parse()
            df = df[df[self.filter_column]]
            assert ID_COL in df.columns, f"measurements spreadsheet does not have a column named {ID_COL}"
            df[ID_COL] = df[ID_COL].str.split('.').str[:-1].str.join('.')
            res = df.set_index(ID_COL)

        logging.debug(f'using meioitic stage names from {p}')

        self.stage_frame = res

    def apply(self, fn, segments):
        '''
        '''
        if fn.stem not in self.stage_frame.index:
            return None

        # add a column of indexes (initially all 0) to the names
        segments['i'] = np.zeros(len(segments), dtype=int)

        # define a Series where values are the names of points that mark ends of stages
        cols = self.stage_frame.loc[fn.stem][self.stage_columns]

        # iterate over the point names, updating the index of any row that has
        # a starting point past the point name
        for p in cols:
            mask = segments.seg_name >= p
            segments.loc[mask,'i'] += 1

        # add a column for the stage name
        segments['stage'] = segments['i'].apply(lambda n: self.stage_names[n])

        return segments[['stage']]


    # def rename_stages(self, df):
    #     '''
    #     Update the stage column in a data frame.  For rows where the stage is
    #     PMT or TZ the stage is the same.  For cells that have PACH in the stage
    #     column change the stage to EP, MP, or LP.  Find the linearized distance 
    #     from the first cell in PACH to the last cell, divide by 3, and set the 
    #     stage of the first third to EP, the second third to MP, and the rest to LP.

    #     Arguments:
    #         df:  the data frame with distance columns

    #     Returns:
    #         a copy of df with the stage column updated with new names
    #     '''
    #     sf = self.stage_frame
    #     blocks = []
    #     for s in ['PMT','TZ']:
    #         sn = set(sf[sf['stage']==s].name)
    #         blk = df[df.seg_name.isin(sn)]
    #         blk['stage'] = s
    #         blocks.append(blk)
    #     sn = set(sf[sf['stage']=='PACH'].name)
    #     blk = df[df.seg_name.isin(sn)]
    #     delta = (blk['pathloc'].max() - blk['pathloc'].min()) / 3
    #     a = blk['pathloc'].min()
    #     for s in ['EP','MP','LP']:
    #         b = a + delta
    #         pf = df[(df.pathloc >= a) & (df.pathloc <= b)]
    #         pf['stage'] = s
    #         blocks.append(pf)
    #         a += delta

    #     res = pd.concat(blocks)
    #     logging.info(f'  renamed meiotic stages for {len(res)} cells')
    #     return res

