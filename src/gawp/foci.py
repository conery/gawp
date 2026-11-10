#
# Definition of Foci, the Geometry subclass for positions of cells
#

import geopandas as gp
import numpy as np
import pandas as pd
from shapely.geometry import Point

from .io import fetch_sheet
from .geometry import GeoBase
from .plugin import Plugin


class Foci(GeoBase):

    fields = {
        'category': 'Surface',
        'index': ['Surpass Object','ID'],
    }

    def __init__(self, **kwargs):
        super().__init__(Foci.fields,kwargs)

    @staticmethod
    def defaults():
        return Plugin.defaults("geometry.foci", Foci.fields)

    def apply(self, xls):
        '''
        Fetch the position sheet from the XLS file, get the locations of foci,
        return them in a GeoPandas frame.

        Arguments:
            xls: an ExcelFile object
        
        Returns:
            a GeoDataFrame containing unique IDs for each measurement ppint and a Point object with the
            x and y coordinates of the measurement.
        '''
        pf = fetch_sheet(
            f = xls,
            name = self.sheet_name,
            id_cols = self.index,
            filter = [self.category_column, self.category]
        )
        self._raw_data = pf

        return gp.GeoDataFrame({
            'point': [Point(pf.iloc[i][self.x_coord], pf.iloc[i][self.y_coord]) for i in range(len(pf))]
        }).set_index(pf.index).set_geometry('point')

