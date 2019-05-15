import os
import numpy as np
import collections
import pickle
import sys
import psutil as ps
import random
import csv
import json
from timeseries import TimeSeries


class old_Utils(object):

    SHAPELET_DIRNAME = "/UniShapelets/"
    SHAPELET_EXT = ".shapelet"
    SEQUENCE_DIRNAME = "/Sequences/"
    SEQUENCE_EXT = ".sequence"
    CSV_DIRNAME = "/csv_shapelet/"
    CSV_EXT = ".csv"
    JSON = SEQUENCE_DIRNAME + "json/"

    @staticmethod
    def convert_csv_to_multivariate_timeseries(directory):

        files_list = [f for f in os.listdir(directory) if f.lower().endswith('.csv')]
        list_multivariate_timeseries = []

        for file in files_list:

            multivariate_timeseries = TimeSeries.generate_from_file(directory, file)
            list_multivariate_timeseries.append(multivariate_timeseries)

        return list_multivariate_timeseries

    # @staticmethod
    # def save_shapelets(directory, list_shapelets):
    #     shapelet_dir = directory + old_Utils.DIRNAME
    #     if not os.path.exists(shapelet_dir):
    #         os.makedirs(shapelet_dir)
    #     for aShapelet in list_shapelets:
    #         file_name = aShapelet.name + aShapelet.dimension_name + old_Utils.EXTENSION
    #         path = shapelet_dir + file_name
    #         pickle.dump(aShapelet, open(path, "wb"))

    @staticmethod
    def save_json(directory, list_sequences):
        folder = directory + old_Utils.JSON
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            files_list = [f for f in os.listdir(folder) if f.lower().endswith('.json')]
            for file in files_list:
                path = folder + file
                os.remove(path)
        for aSequence in list_sequences:
            file_name = str(aSequence.name) + aSequence.dimension_name + '.json'
            path = folder + file_name
            with open(path, 'w') as outfile:
                outfile.write(aSequence.__repr__())
                # j = jsonpickle.encode(aSequence.sequence[0], make_refs=False)
                # outfile.write(j)
                # outfile.flush()
                # outfile.close()

    @staticmethod
    def json_list(representation, name, listos):
        representation += '"' + name + '":['
        for s in listos:
            representation += '' + str(s) + ','
        if len(listos):
            representation = representation[:-1]
        representation += ']'
        return representation

    @staticmethod
    def json_dict(representation, name, dictos, key='list'):
        representation += '"' + name + '":{'
        for k, i in dictos.items():
            if key == 'list':
                representation = old_Utils.json_list(representation, k, i)
                representation += ','
            else:
                representation += '"' + k + '": '
                representation += '' + str(i) + ','
        representation = representation[:-1]
        representation += '}'
        return representation


    @staticmethod
    def save(directory, list_objects, option):
        if option.lower() == 'shapelet':
            dirname = old_Utils.SHAPELET_DIRNAME
            extension = old_Utils.SHAPELET_EXT
        elif option.lower() == 'sequence':
            dirname = old_Utils.SEQUENCE_DIRNAME
            extension = old_Utils.SEQUENCE_EXT
        elif option.lower() == 'csv':
            dirname = old_Utils.CSV_DIRNAME
            extension = old_Utils.CSV_EXT
        folder = directory + dirname
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            ##clean the historical files
            files_list = [f for f in os.listdir(directory + dirname) if f.lower().endswith(extension)]
            for file in files_list:
                path = directory + dirname + file
                os.remove(path)

        if option.lower() != 'csv':
            for anObject in list_objects:
                file_name = str(anObject.name) + anObject.dimension_name + extension
                path = folder + file_name
                pickle.dump(anObject, open(path, "wb"))
        else:
            file_name = "shapelet_test" + extension
            path = folder + file_name
            i = 0
            with open(path, 'w') as f:
                writer = csv.writer(f, lineterminator='\n', delimiter=';',)
                for anObject in list_objects:
                    i+=1
                    for key in anObject.matching_indices:
                        writer.writerow(["shapelet" + str(i), anObject.name, anObject.dimension_name, anObject.class_shapelet, key, anObject.matching_indices[key], anObject.gain, anObject.subsequence.tolist(),  anObject.min_distance] )

    @staticmethod
    def load(directory, option):
        if option.lower() == 'shapelet':
            dirname = old_Utils.SHAPELET_DIRNAME
            extension = old_Utils.SHAPELET_EXT
        elif option.lower() == 'sequence':
            dirname = old_Utils.SEQUENCE_DIRNAME
            extension = old_Utils.SEQUENCE_EXT
        files_list = [f for f in os.listdir(directory + dirname) if f.lower().endswith(extension)]
        list_objects = []
        for file in files_list:
            path = directory + dirname + file
            an_object = pickle.load(open(path, "rb"))
            list_objects.append(an_object)
        return list_objects

    # @staticmethod
    # def load_shapelets(directory):
    #     files_list = [f for f in os.listdir(directory + old_Utils.DIRNAME) if f.lower().endswith(old_Utils.EXTENSION)]
    #     list_shapelets = []
    #     for file in files_list:
    #         path = directory + old_Utils.DIRNAME + file
    #         shapelet = pickle.load(open(path, "rb"))
    #         list_shapelets.append(shapelet)
    #     return list_shapelets

    # A helper generator method to create a sliding window over a list and return all the sub-lists
    @staticmethod
    def sliding_window(sequence, win_size, step=1):
        # Verify the inputs
        try:
            it = iter(sequence)
        except TypeError:
            raise Exception("**ERROR** sequence must be iterable.")
        if not ((type(win_size) == type(0)) and (type(step) == type(0))):
            raise Exception("**ERROR** type(winSize) and type(step) must be int.")
        if step > win_size:
            raise Exception("**ERROR** step must not be larger than winSize.")
        if win_size > len(sequence):
            raise Exception("**ERROR** winSize must not be larger than sequence length.")

        # Pre-compute number of chunks to emit
        num_chunks = ((len(sequence) - win_size) / step) + 1

        # Do the work
        for i in range(0, int(num_chunks * step), step):
            yield sequence[i:i + win_size]

    # A helper method that helps to calculate the entropy
    @staticmethod
    def entropy_helper(n):
        return - (n * np.log2(n))

    # A helper method to calculate the entropy of the data set
    @staticmethod
    def dataset_entropy(unid):
        classes_dict = collections.defaultdict(list)
        for timeseries in unid:
            classes_dict[timeseries.class_timeseries].append(timeseries)
        entropy = 0.0
        for key in classes_dict.keys():
            #print("key class is ", str(key))
            p = float(len(classes_dict[key])) / len(unid)
            #print("p is ", str(p))
            entropy += old_Utils.entropy_helper(p)
        #print("entropy is ", entropy)
        return entropy

    @staticmethod
    def entropy_after_split(unid1, unid2):
        f1 = float(len(unid1)) / (len(unid1) + len(unid2))
        f2 = float(len(unid2)) / (len(unid1) + len(unid2))
        #print("f1 is ", str(f1), "f2 is", str(f2))
        entropy1 = f1 * old_Utils.dataset_entropy(unid1)
        #e1class = [ts.class_timeseries for ts in unid1]
        #e2class = [ts.class_timeseries for ts in unid2]
        #print("unid1.class is: ", e1class)
        #print("unid2.class is: ", e2class)
        entropy2 = f2 * old_Utils.dataset_entropy(unid2)
        #print("entropy1 + entropy2 is ", entropy1 + entropy2)
        return entropy1 + entropy2

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
    def min_length_dataset(list_timeseries):
        min_l = sys.maxsize
        for mts in list_timeseries:
            if len(mts.timeseries) < min_l:
                min_l = len(mts.timeseries)
        return min_l

    @staticmethod
    def max_length_dataset(list_multivariate_timeseries):
        max_l = 0
        for mts in list_multivariate_timeseries:
            if mts.length() > max_l:
                max_l = mts.length()
        return max_l

    @staticmethod
    def check_memory(perc=90):
        mem = ps.virtual_memory()
        if mem.percent >= perc:
            return False
        return True

    @staticmethod
    def get_random_color(pastel_factor=0.5):
        return [(x + pastel_factor) / (1.0 + pastel_factor) for x in [random.uniform(0, 1.0) for i in [1, 2, 3]]]

    @staticmethod
    def color_distance(c1, c2):
        return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])

    @staticmethod
    def generate_new_color(existing_colors, pastel_factor=0.5):
        max_distance = None
        best_color = None
        for i in range(0, 100):
            color = old_Utils.get_random_color(pastel_factor=pastel_factor)
            if not existing_colors:
                return color
            best_distance = min([old_Utils.color_distance(color, c) for c in existing_colors])
            if not max_distance or best_distance > max_distance:
                max_distance = best_distance
                best_color = color
        return best_color

    @staticmethod
    def generate_new_colors(k=10):
        colors = []
        for i in range(k):
            colors.append(old_Utils.generate_new_color(colors, pastel_factor=0.9))
        return colors
