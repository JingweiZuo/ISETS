import numpy as np
from collections import defaultdict
import sys
from typing import Any

class TimeSeries(object):
    def __init__(self):
        self.class_timeseries = ''
        self.dimension_name = ''
        self.discmP = {}
        self.threshP = {}
        self.timeseries = None
        self.matched = False
        self.name = ''


    def __repr__(self):
        representation = "Timeseries with dimension: " + self.dimension_name
        representation += " with class: " + str(self.class_timeseries)
        representation += " with series: " + str(self.timeseries)
        return representation

    def __str__(self):
        representation = "Timeseries with dimension: " + self.dimension_name
        representation += " with class: " + str(self.class_timeseries)
        representation += " with series: " + str(self.timeseries)
        return representation

    @staticmethod
    def groupByClass_timeseries(list_timeseries):
        #'list_timeseries': {ts_name1:ts1, ts_name2:ts2, ...}
        dict_ts = {}  # type: dict
        for ts in list_timeseries.values():
            ts_class = ts.class_timeseries
            if ts_class in dict_ts.keys():
                dict_ts[ts.class_timeseries].append(ts)
            else:
                dict_ts[ts.class_timeseries] = [ts]
        return dict_ts


