"""
gawp.linearize

Main steps in the linearization algorithm
"""

import geopandas as gp
import logging
import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString

from .config import Config


def create_segments(mf: pd.DataFrame, sd: dict):
    '''
    Make a frame where rows contain descriptions of line segments made by connecting
    adjacent measurement points.  Columns have attributes of each
    segment, including the parameters of the linear equation and segment length.

    Arguments:
        mf:  a data frame with names and locations of measurement points
        sd:  (optional) a dictionary with meiotic stage definitions

    Returns:
        a Pandas frame with line segments and their equations and lengths.
    '''
    PMT_NAME = Config.MeioticStage.stage_names[0]
    TZ_NAME = Config.MeioticStage.stage_names[1]

    def orientation(sp, ep):
        'Helper function, determines orientation of line from sp to ep'
        if ep.x > sp.x:
            res = 'NE' if ep.y > sp.y else 'SE'
        else:
            res = 'NW' if ep.y > sp.y else 'SW'
        return res

    df = gp.GeoDataFrame({
        'name': [mf.loc[i]['name'] + mf.loc[i+1]['name'] for i in range(len(mf)-1)],
        'head': [mf['point'].loc[i] for i in range(len(mf)-1)],
        'tail': [mf['point'].loc[i+1] for i in range(len(mf)-1)],
    }).set_geometry('head').set_geometry('tail')

    df['segment'] = [LineString([df['head'][i],df['tail'][i]]) for i in range(len(df))]
    df['orientation'] = [orientation(df['head'][i],df['tail'][i]) for i in range(len(df))]
    df['A'] = ((df['tail'].y - df['head'].y) / (df['tail'].x - df['head'].x))
    df['C'] = df['head'].y - df['head'].x*df['A']
    df['length'] = Point.distance(df['head'], df['tail'])
    df['pathlen'] = np.cumulative_sum(df['length'], include_initial=True)[:-1]
    df['stage'] = [('PMT' if p < sd[PMT_NAME] else 'TZ' if p < sd[TZ_NAME] else 'PACH') for p in mf['name'][0:-1]]
   
    return df.set_geometry('segment')

def linearize(args, fn):
    '''
    Top level function of the linearization algorithm on one file.

    Arguments:
        args:  command line arguments
        files:  the path to a spreadsheets with Imaris data
    '''
    logging.info(f'linearize {fn}')

