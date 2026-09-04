"""
gawp.linearize

Main steps in the linearization algorithm
"""

from pathlib import Path

import geopandas as gp
import logging
import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString

from gawp.config import config
import gawp.io as io

##########################
#
# linearize
#

def linearize(args):
    '''
    Top level function of the linearization algorithm.  Reads the meitotic
    stage spreadsheet, then runs the linearization pipeline on all data files.
    
    Arguments:
        args:  command line arguments
        fn:    path to a spreadsheet with Imaris data
    '''
    output_dir = io.make_output_dir(args)
    stage_frame = io.read_stages()
    for fn in io.get_spreadsheet_names(args):
        nuclei, measurements = read_data(fn)
        stages = select_stage(fn, stage_frame) if stage_frame is not None else None
        segments = create_segments(measurements, stages)
        product = gp.GeoDataFrame.join(nuclei, segments, how="cross")
        distances = compute_distances(product)
        merged = minimum_distance(distances, product)
        print(merged.head())


##########################
#
# Pipeline step:  read the cell and measurement locations from the data file
#

def read_data(fn):
    '''
    Get the position data from the spreadsheet, return two dataframes, one
    for the rows that have cell positions and one for rows with measurement
    positions.
    '''
    df = io.read_positions(fn)

    cf = io.get_cell_positions(df)
    logging.info(f'  {len(cf)} cell positions')

    mf = io.get_measurement_positions(df)
    logging.info(f'  {len(mf)} measurement positions')

    return cf, mf

##########################
#
# Pipeline step:  create a dictionary with the meiotic stages of the current
# data set.
#

def select_stage(fn, sf):
    '''
    Find the row in the stage frame for the current input file.

    Arguments:
        fn: the name of the spreadsheet file for the current data set
        sf: a data frame read from the measurements spreadsheet

    Returns:
        a dictionary that maps a stage name to the measurement point where that
        stage begins.
    '''
    id = Path(fn).stem
    if id in sf.index:
        row = sf.loc[id]
        stages = {s:row[s] for s in config.meioticstage.stage_names}
    else:
        logging.warning(f'  no row for {id} in meotic stage frame, stages will not be assigned')
        stages = {}

    logging.info(f'  meiotic stages: {stages}')
    return stages

##########################
#
# Pipeline step: create line segments from the measurement data
#

def create_segments(mf: pd.DataFrame, sd: dict):
    '''
    Make a frame where rows contain descriptions of line segments made by connecting
    adjacent measurement points.  Columns have attributes of each
    segment, including the parameters of the linear equation and segment length.

    Arguments:
        mf:  a data frame with names and locations of measurement points
        sd:  a dictionary with meiotic stage definitions (can be None)

    Returns:
        a Pandas frame with line segments and their equations and lengths.
    '''
    PMT_NAME = config.meioticstage.stage_names[0]
    TZ_NAME = config.meioticstage.stage_names[1]

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
    if sd:
        df['stage'] = [('PMT' if p < sd[PMT_NAME] else 'TZ' if p < sd[TZ_NAME] else 'PACH') for p in mf['name'][0:-1]]
   
    return df.set_geometry('segment')

##########################
#
# Pipeline step: compute distances between cells and segments
#

def compute_distances(df: gp.GeoDataFrame):
    '''
    Create a new frame that summarizes the distances between nuclei and line segments.  The
    columns in the new frame will be:
    * `nuc_id`, the nucleus ID
    * `seg_name`, the name of the segment
    * `distance`, the distance from the nucleus to the segment
    * `intersection`, a string that identifies where the nucleus is closest (head, tail, middle of the segment)
    
    The function computes three distances for each cell/segment combination: the distance to the head of the
    segment, the distance to the tail, and the distance to the line connecting the two.  The shortest
    of these three is saved as the distance between the cell and the segment.
    
    Arguments:
      df: a GeoDataFrame that has the line segments and their equations

    Returns:
      a frame with the distance values
    '''
    
    pos = gp.GeoDataFrame({
        'head': gp.GeoDataFrame.distance(df['point'],df['head']),
        'tail': gp.GeoDataFrame.distance(df['point'],df['tail']),
        'mid': gp.GeoDataFrame.distance(df['point'],df['segment']),
    })

    res = gp.GeoDataFrame({
        'nuc_id': df['id'],
        'seg_name': df['name'],
        'distance': pos.min(axis='columns'),
        'intersection': pos.idxmin(axis='columns')
    })

    return res

##########################
#
# Pipeline step: find the closest segment to each cell
#

def minimum_distance(df: gp.GeoDataFrame, cpf: gp.GeoDataFrame):
    '''
    Form groups based on cell ID, and then find the row in each group that has the
    shortest distance to a line segment.  Save the **row numbers** of those rows in a
    frame called `locs`.

    Then use those row numbers to select the corresonding rows from the combined data
    to create a frame that has the complete cell and segment data for the seleced rows.

    Arguments:
        df: the data frame with all distance combinations
        cpf: the cross product frame
    '''
    locs = df.groupby('nuc_id')[['distance']].idxmin()
    return gp.GeoDataFrame(df.loc[locs.distance].join(cpf[['point','head','tail','orientation','A','C','pathlen']]))
