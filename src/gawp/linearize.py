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

from .config import config
from .io import parse_positions, read_stages, get_measurement_positions, get_cell_positions


def linearize(args):
    '''
    Top level function of the linearization algorithm.  Reads the meitotic
    stage spreadsheet, then runs the linearization pipeline on all data files.
    
    Arguments:
        args:  command line arguments
        fn:    path to a spreadsheet with Imaris data
    '''
    output_dir = make_output_dir(args)
    stage_frame = get_stage_data()
    for fn in get_spreadsheet_names(args):
        run_pipeline(fn, output_dir, stage_frame, args.preview)

def get_stage_data():
    '''
    Find the name of the meiotic stage spreadsheet in the config file,
    read the spreadsheet.
    '''
    if fn := config.imaris.measurements:
        p = Path(fn).resolve()
        if not p.is_file():
            logging.warn(f'imaris.measurements "{fn}": file not found')
            res = None
        else:
            with pd.ExcelFile(p, engine='calamine') as f:
                res = read_stages(f)
    else:
        logging.warn(f'config has no value for imaris.measurement')
        res = None

    if res is None:
        logging.warn('meiotic stages will not be assigned')
    else:
        logging.info(f'using meioitic stage names from {p}')

    return res

def get_spreadsheet_names(args):
    '''
    Return a list of names of spreasheets with Imaris data.

    File names from the command line take precedence over names from the 
    config file.  Warns the user if a file does not exist.

    Arguments:
        args:  command line arguments

    Returns:
        a list of paths to spreadsheeets
    '''
    if args.file:
        globbed = [f.resolve() for f in args.file]
    elif config.imaris.data:
        globbed = [f.resolve() for p in config.imaris.data.split() for f in Path('.').glob(p)]
        if len(globbed) == 0:
            raise ValueError(f'no files match pattern from imaris.data: "{config.imaris.data}"')
    else:
        raise ValueError('Specify path to input data in configuration or with --file')

    res = []
    for fn in globbed:
        if Path.is_dir(fn):
            logging.warn(f'ignoring directory name {fn}; use {fn}/* to specify all files in a directory')
            continue
        if not Path.exists(fn):
            logging.warn(f'file not found: {fn}')
            continue
        res.append(fn)

    return res

def make_output_dir(args):
    '''
    Return the path to the directory where outputs will be written.  A name
    specified on the command line takes precedence over a name in the config
    file.  Creates the directory if it does not exist.

    Arguments:
        args:  command line arguments

    Returns:
        a list of paths to spreadsheeets
    '''
    fn = args.output or config.output.data
    if not fn:
        raise ValueError('specify an output directory in the config file or with --output')

    p = Path(fn).resolve()
    try:
        p.mkdir(parents=True, exist_ok=True)
    except FileExistsError as err:
        logging.error(f"can't use {fn} for directory name; there is an existing file named {p}")
        raise ValueError("choose a different output name or rename/delete the existing file")

    logging.info(f'output directory: {p}')
    return p

def run_pipeline(fn, out, sf, pre):
    '''
    Execute all steps of the linearization algorithm.

    Arguments:
        fn:    path to a spreadsheet with Imaris data
        out:   path to the output directory
        sf:    frame with meiotic stage data
        pre:   if True print log but don't execute the steps
    '''
    logging.info(f'linearize {fn}')

    # Open the spreadsheet, read the position and measurement data
    with pd.ExcelFile(fn, engine="calamine") as f:
        df = parse_positions(f)
        nuclei = get_cell_positions(df)
        measurements = get_measurement_positions(df)
        logging.info(f'  {len(nuclei)} cell positions')
        logging.info(f'  {len(measurements)} measurement positions')

    # Get the meiotic stages for this data set
    id = Path(fn).stem
    if id in sf.index:
        row = sf.loc[id]
        stages = {s:row[s] for s in config.meioticstage.stage_names}
        logging.info(f'  meiotic stages: {stages}')
    else:
        logging.warning(f'  no row for {id} in meotic stage frame, stages will not be assigned')

# 


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
    df['stage'] = [('PMT' if p < sd[PMT_NAME] else 'TZ' if p < sd[TZ_NAME] else 'PACH') for p in mf['name'][0:-1]]
   
    return df.set_geometry('segment')
