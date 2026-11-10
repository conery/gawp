#
# Definition of Measurements, the Geometry subclass for positions of measurement points
#

import geopandas as gp
import numpy as np
import pandas as pd
from shapely.geometry import Point, LineString

from .io import fetch_sheet
from .geometry import GeoBase
from .plugin import Plugin

class Measurements(GeoBase):

    fields = {
        'category': 'MeasurementPoint',
        'index': 'Name',
    }

    def __init__(self, **kwargs):
        super().__init__(Measurements.fields,kwargs)

    @staticmethod
    def defaults():
        return Plugin.defaults("geometry.measurements", Measurements.fields)

    def apply(self, xls):
        '''
        Extract the measurement locations from the Position sheet in.

        Arguments:
            xls: an ExcelFile object
        
        Returns:
            a GeoDataFrame containing unique IDs for each measurement point and a Point object with the
            x and y coordinates of the measurement.
        '''
        pf = fetch_sheet(
            f = xls,
            name = self.sheet_name,
            filter = [self.category_column, self.category]
        )
        pf.index = range(len(pf))
        self._raw_data = pf

        return gp.GeoDataFrame({
            'name': pf[self.index],
            'point': [Point(pf.loc[i][self.x_coord], pf.loc[i][self.y_coord]) for i in range(len(pf))]
        }).set_geometry('point') 

    def create_segments(self, pf):
        '''
        Iterate over the measurement points to create line segments connecting
        the points.  The results are returned as a data frame

        Arguments:
            pf: a frame containing measurement points

        Returns:
            a GeoDataFrame with line segments connecing adjacent points
        '''

        def orientation(sp, ep):
            'Helper function, determines orientation of line from sp to ep'
            if ep.x > sp.x:
                res = 'NE' if ep.y > sp.y else 'SE'
            else:
                res = 'NW' if ep.y > sp.y else 'SW'
            return res

        df = gp.GeoDataFrame({
            'name': [pf.loc[i]['name'] + pf.loc[i+1]['name'] for i in range(len(pf)-1)],
            'head': [pf['point'].loc[i] for i in range(len(pf)-1)],
            'tail': [pf['point'].loc[i+1] for i in range(len(pf)-1)],
        }).set_geometry('head').set_geometry('tail')

        df['segment'] = [LineString([df['head'][i],df['tail'][i]]) for i in range(len(df))]
        df['orientation'] = [orientation(df['head'][i],df['tail'][i]) for i in range(len(df))]

        return df.set_geometry('segment')

    def add_equations(self, df):
        '''
        Add equations for slope and other info needed to compute the distance
        between foci and line segments

        Arguments:
            df: the frame to update
        '''
        df['A'] = ((df['tail'].y - df['head'].y) / (df['tail'].x - df['head'].x))
        df['C'] = df['head'].y - df['head'].x*df['A']
        df['length'] = Point.distance(df['head'], df['tail'])
        df['pathlen'] = np.cumulative_sum(df['length'], include_initial=True)[:-1]

