#
#
# Plugin for geometry calculations.  Two classes are defined here:
#   GeoBase is the base class for the two kinds of geometry data (Foci and Measurements)
#   Geometry defines the plugin that has methods that implement steps of the linearization algorithm
#

import logging

import geopandas as gp
import numpy as np
import pandas as pd
from shapely.geometry import Point

from .plugin import Plugin

class GeoBase(Plugin):
    '''
    Define fields found in all subclasses 
    '''

    fields = {
        'sheet_name': 'Position',
        'category_column': 'Category',
        'x_coord': 'Position X',
        'y_coord': 'Position Y',
    }

    def __init__(self, fields, kwargs):
        '''
        Combine the fields defined in the subclass with the fields defined
        here to instantiate a subclass object.
        '''
        super().__init__(GeoBase.fields|fields, kwargs)
        logging.debug(f'geobase {fields} {kwargs}')

class Geometry:

    def __init__(self, foci, measures):
        '''
        Initializations for linearization calculations.

        Arguments:
            foci:  an instance of the Foci subclass
            measures:  an instance of the Measurements subclass
        '''
        self.foci = foci
        self.measurements = measures
        self.position_frame = None
        self.segment_frame = None
        self.linearized_frame = None

    @staticmethod
    def defaults():
        return Plugin.defaults("geometry", Geometry.fields)

    def apply(self, xls):
        '''
        Fetch the position sheet from the XLS file, get the locations of foci,
        return them in a data frame.
        '''
        self.position_frame = self.foci.apply(xls)
        logging.info(f'  geometry.position_frame: {len(self.position_frame)} foci')

        if self.measurements:
            self.measurements_frame = self.measurements.apply(xls)
            self.segment_frame = self.measurements.create_segments(self.measurements_frame)
            self.measurements.add_equations(self.segment_frame)
            logging.info(f'  geometry.measurements_frame: {len(self.measurements_frame)} points')
        else:
            logging.warn(f'  no measurements')
        
        return self.position_frame

    def linearize(self, include_stages=True):
        '''
        Create a frame that combines the positions with the line segments, compute
        distances from each point to each line segment, then find the minimum distance.
        '''
        # If the app didn't ask for measurements just save the foci
        if self.measurements is None:
            self.linearized_frame = self.position_frame
            return

        # add the index (the unique identifier for each data point) as a column named 'uid'
        positions = self.position_frame.reset_index(names='uid')

        # create all combinations of points and segments
        product = gp.GeoDataFrame.join(positions, self.segment_frame, how="cross")

        # compute the distance for each combination
        distances = self.compute_distances(product)

        # # copy the stages column if the app uses it
        # if include_stages:
        #     distances['stage'] = product['stage']

        # find the minimum distance, save info about where the distance was found
        merged = self.minimum_distance(distances, product)

        # append a column with the normalized locations
        self.add_normalized_locations(merged, self.segment_frame)

        # all done, save the result for future plugins
        self.linearized_frame = merged.set_index('uid')

    def compute_distances(self, df: gp.GeoDataFrame):
        '''
        Create a new frame that summarizes the distances between nuclei and line segments.  The
        columns in the new frame will be:
        * `uid`, unique identifiers for foci
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
            'uid': df['uid'],
            'seg_name': df['name'],
            'distance': pos.min(axis='columns'),
            'intersection': pos.idxmin(axis='columns')
        }).set_index(df.index)

        logging.info(f'  added distances to {len(res)} combinations')
        return res

    def minimum_distance(self, df: gp.GeoDataFrame, cpf: gp.GeoDataFrame):
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
        output_cols = ['uid','seg_name','point','head','tail','distance','orientation','pathlen','loc','pathseg']

        # find the row number with the minimum distance for each cell
        locs = df.groupby('uid')[['distance']].idxmin()

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

    def add_normalized_locations(self, df: gp.GeoDataFrame, sf: pd.DataFrame):
        '''
        Add a new column to the data set that shows the total distance from the
        start of the germline to each intersection point, normalized by the total
        length of the germline.

        Argument:
            df: a data frame with intersection columns
            sf: the frame with line segments
        '''
        scale = np.sum(sf['length'])
        df['pathloc'] = (df['pathlen'] + df['pathseg']) / scale
        logging.info(f'  normalized paths for {len(df)} cells')

    def add_columns(self, df):
        '''
        Append columns collected by another plugin.  Assumes that plugin
        uses the same indexing scheme.

        Arguments:
            df: a data frame created by another plugin
        '''
        self.linearized_frame = self.linearized_frame.join(df)
        logging.info(f'  added {list(df.columns)} to position_frame')

