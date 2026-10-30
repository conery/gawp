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
# Top level function.  Pass the command line arguments to this function, it will
# open each Imaris spreadsheet, import the data points, and run the full pipeline
# on all data sets.
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
        logging.info(f'[bold blue]Linearizing {fn.stem}')
        nuclei, measurements = read_data(fn)
        stages = select_stage(fn, stage_frame) if stage_frame is not None else None
        segments = create_segments(measurements, stages)
        product = gp.GeoDataFrame.join(nuclei, segments, how="cross")
        distances = compute_distances(product)
        merged = minimum_distance(distances, product)
        add_normalized_locations(merged, segments)
        final = rename_stages(merged, segments) if stages else merged
        logging.info(f'  saving {len(final)} linearized data points')
        # print(final.head())


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

    logging.info(f'  added geometry columns to {len(df)} rows')
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

    logging.info(f'  added distances to {len(res)} combinations')
    return res

##########################
#
# Pipeline step: find the closest segment to each cell
#

def minimum_distance(df: gp.GeoDataFrame, cpf: gp.GeoDataFrame):
    '''
    Form groups in the distance frame based on cell ID, and then find the row in 
    each group that has the shortest distance to a line segment.  Select rows from
    the cross product that have the shortest distances, compute the intersection 
    points, and add the distance from the start of the segment to the intersection point.

    Arguments:
        df: the data frame with all distance combinations
        cpf: the cross product frame

    Returns:
        a frame with one row per cell along with new columns for the distances
    '''
    # define a list of names of columns to include in the result frame
    output_cols = ['nuc_id','seg_name','point','head','tail','distance','orientation','pathlen','loc','pathseg']
    # if 'stage' in cpf.columns:
    #     output_cols.append('stage')

    # find the row number with the minimum distance for each cell
    locs = df.groupby('nuc_id')[['distance']].idxmin()

    # make a temporary frame that has the rows from the combined frame, using the
    # locations computed above
    tdf = gp.GeoDataFrame(df.loc[locs.distance].join(cpf[['point','head','tail','orientation','A','C','pathlen']]))

    # separate the rows by intersection type; compute the perpendicular intersections
    # where the closest point is in the middle, or use one of the end points when the
    # closest point is the head or tail.
    mids = tdf[tdf['intersection']=='mid']
    xp = (mids.point.y - (-mids.point.x/mids.A) - mids.C) / (mids.A - (-1/mids.A))
    yp = (-xp/mids.A) + mids.point.y - (-mids.point.x/mids.A)
    mids['loc'] = [Point(xp.iloc[i],yp.iloc[i]) for i in range(len(mids))]

    heads = tdf[tdf['intersection']=='head']
    heads['loc'] = heads['head']

    tails = tdf[tdf['intersection']=='tail']
    tails['loc'] = tails['tail']

    # concatenate the three groups into a single frame and add a column
    # for the distance from the start of the segment to the intersection point
    res = pd.concat([mids,heads,tails]).set_geometry('loc')
    res['pathseg'] = gp.GeoDataFrame.distance(res['head'], res['loc'])
    
    logging.info(f'  minimium distances for {len(res)} cells')
    return res[output_cols]

##########################
#
# Pipeline step: compute normalized positions
#

def add_normalized_locations(df: gp.GeoDataFrame, sf: pd.DataFrame):
    '''
    Add a new column to the data set that shows the total distance from the
    start of the germline to each intersection point, normalized by the total
    length of the germline.

    Argument:
        df: a data frame with intersection columns
    '''
    scale = np.sum(sf['length'])
    df['pathloc'] = (df['pathlen'] + df['pathseg']) / scale

    logging.info(f'  normalized paths for {len(df)} cells')


##########################
#
# Pipeline step: add meioitic stage names to each point
#

def rename_stages(df, sf):
    '''
    Update the stage column to the data frame.  For rows where the stage is
    PMT or TZ the stage is the same.  For cells that have PACH in the stage
    column change the stage to EP, MP, or LP.  Find the linearized distance 
    from the first cell in PACH to the last cell, divide by 3, and set the 
    stage of the first third to EP, the second third to MP, and the rest to LP.

    Arguments:
        df:  the data frame with distance columns
        sf:  the frame with segment definitions

    Returns:
        a copy of df with the stage column updated with new names
    '''
    blocks = []
    for s in ['PMT','TZ']:
        sn = set(sf[sf['stage']==s].name)
        blk = df[df.seg_name.isin(sn)]
        blk['stage'] = s
        blocks.append(blk)
    sn = set(sf[sf['stage']=='PACH'].name)
    blk = df[df.seg_name.isin(sn)]
    delta = (blk['pathloc'].max() - blk['pathloc'].min()) / 3
    a = blk['pathloc'].min()
    for s in ['EP','MP','LP']:
        b = a + delta
        pf = df[(df.pathloc >= a) & (df.pathloc <= b)]
        pf['stage'] = s
        blocks.append(pf)
        a += delta

    res = pd.concat(blocks)
    logging.info(f'  meiotic stages for {len(res)} cells')
    return res
