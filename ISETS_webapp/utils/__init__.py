import os
import numpy as np
import collections
import pickle
import sys
import random
import csv
import json
import utils.timeseries

class Shapelet(object):
    def __init__(self):
        self.id = 0.0
        self.Class = ''
        self.subseq = None
        self.DD = 0.0
        self.thresh = 0.0

class Dataset(object):
    def __init__(self):
        self.name = "test"
        self.ClassList = []
        self.size = 0
        self.tslength = 0
        self.queryLength = []
        self.queryIndex = []
        self.tsNameDir = {} #TS+number : Hash name of TS
        self.tsNbrList = [] #TS_number list

    def update(self, array_tsdict, datasetname):
        self.name = datasetname
        # "array_tsdict": [ {HashName: tsObject} ]
        self.tsObjectDir = {key: value for element in array_tsdict for key, value in element.items()}
        HushList = self.tsObjectDir.keys()
        for Hush in HushList:
            self.tsNameDir["ts" + str(self.size)] = Hush  # ts.name here is a hash number, should be converted into a simple interger
            self.ClassList.append(self.tsObjectDir[Hush].class_timeseries)
            self.size += 1
        self.tsNbrList = list(self.tsNameDir.keys())
        self.ClassList = list(set(self.ClassList))
        self.tslength = len(self.tsObjectDir[list(HushList)[0]].timeseries)
        self.queryLength = list(range(self.tslength//2))
        # the index will be changed along with the query's length
        #self.queryIndex = list(range(0, self.tslength - v_queryLength))

    def ts_object(self, ts_name):
        #return the TS object
        hush = self.tsNameDir(ts_name)
        return self.tsObjectDir(hush)

class Utils(object):
    @staticmethod
    def load(directory, option):
        dirname = ""
        extension =""
        if option.lower() == "dataset":
            dirname = "/Dataset/"
            extension = ".csv"

        files_list = [f for f in os.listdir(directory + dirname) if f.lower().endswith(extension)]
        list_objects = []
        for file in files_list:
            path = directory + dirname + file
            #an_object = np.genfromtxt(path)
            an_object = np.genfromtxt(path, delimiter = ",")
            list_objects.extend(an_object)
        # return a list[Array_TimeSeries]
        return list_objects

    # if the dataset format is changed, just modify this function to adapt it
    @staticmethod
    def generate_timeseries(directory):
        #list_ts = list[TimeSeries]
        array_ts = []
        list_rawData = Utils.load(directory, 'Dataset')
        for d in list_rawData:
            # d[0] is the class of TS in the original data, d[1:] is the data in TS
            t = timeseries.TimeSeries()
            t.class_timeseries = d[0]
            t.timeseries = d[1:]
            t.name = hash(d[1:].tostring())
            array_ts.append({t.name:t})
        return array_ts

    @staticmethod
    def load_dataset(directory):
        #list_ts = list[TimeSeries]
        array_ts = []
        list_rawData = np.genfromtxt(directory, delimiter=",")
        for d in list_rawData:
            # d[0] is the class of TS in the original data, d[1:] is the data in TS
            t = timeseries.TimeSeries()
            t.class_timeseries = d[0]
            t.timeseries = d[1:]
            t.name = hash(d[1:].tostring())
            array_ts.append({t.name:t})
        return array_ts


    @staticmethod
    def print_progress(iteration, total, prefix='Progress:', suffix='Complete', decimals=1, barLength=70):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            barLength   - Optional  : character length of bar (Int)
        """
        format_str = "{0:." + str(decimals) + "f}"
        percent = format_str.format(100 * (iteration / float(total)))
        filled_length = int(round(barLength * iteration / float(total)))
        bar = '█' * filled_length + '-' * (barLength - filled_length)
        sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
        if iteration == total:
            sys.stdout.write('\n')
        sys.stdout.flush()

    @staticmethod
    def check_memory(perc=90):
        mem = ps.virtual_memory()
        if mem.percent >= perc:
            return False
        return True

    @staticmethod
    def min_length_dataset(list_timeseries):
        min_l = sys.maxsize
        for mts in list_timeseries:
            if len(mts.timeseries) < min_l:
                min_l = len(mts.timeseries)
        return min_l