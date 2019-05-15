from flask import Flask, Blueprint, render_template, request, jsonify
from threading import Thread
import time

account_api = Blueprint('account_api', __name__)
x = 0
y = 0

# Global variable for output GUI
thread = None
t_stamp = 0
loss_batch = 0.0
avg_loss = 0.0
drift = False
inputTSBatch = []
TS_set = []

import numpy as np
import pandas as pd
import similarity_measures as sm
import SMAP.MatrixProfile as mp
import memory_block as mb
import SMAP_block as sb
import evaluation_block as eb
import utils.utils as util
import time, sys

def global_structure(k, data_directory, m_ratio, stack_ratio, window_size):
    list_timeseries = util.load_dataset(data_directory)
    name_dataset = {k: v for ds in list_timeseries for k, v in ds.items()}
    dataset_list = list(name_dataset.values())
    ##############################Modified variable for Web GUI##############################
    global drift, loss_batch, avg_loss, t_stamp, inputTSBatch, TS_set
    min_m = util.min_length_dataset(dataset_list)
    print("Maximum length of shapelet is : " + str(min_m))
    min_length = int(0.1 * min_m)
    max_length = int(0.5 * min_m)
    m_list =range(min_length, max_length, int(min_m * m_ratio))
    stack_size = int(stack_ratio * len(dataset_list))
    TS_set = []
    MP_set_all = {}

    #Initialization of shapList
    driftDetection = eb.driftDetection()
    inputTSBatch = driftDetection.stream_window(dataset_list, window_size)
    TS_newSet, MP_set_all = mb.memory_cache_all_length(TS_set, MP_set_all, stack_size, inputTSBatch, m_list)

    shapList = sb.extract_shapelet_all_length(k, TS_newSet, MP_set_all, m_list)
    output_loss = pd.DataFrame([[0,0,0,0,0,0]], columns=['t_stamp', 'loss_batch', 'cum_loss', 'PH', 'avg_loss', 'nbr_drift'])
    output_shapelet = pd.DataFrame([[0,0,0,0,0]], columns=['t_stamp', 'shap.name', 'shap.Class', 'shap.subseq', 'shap.score'])
    while driftDetection.t_stamp < len(dataset_list):
        inputTSBatch = driftDetection.stream_window(dataset_list, window_size)
        drift, loss_batch, cum_loss, PH, avg_loss = driftDetection.shapelet_matching(shapList, inputTSBatch)
        t_stamp = driftDetection.t_stamp
        if drift == True:
            nbr_drift = 1
        else:
            nbr_drift = 0
            time.sleep(1)
        loss_set = [driftDetection.t_stamp, loss_batch, cum_loss, PH, avg_loss, nbr_drift]
        loss_pd = pd.DataFrame([loss_set],
                                   columns=['t_stamp', 'loss_batch', 'cum_loss', 'PH', 'avg_loss', 'nbr_drift'])
        output_loss = output_loss.append(loss_pd)
        if drift == True:
            TS_newSet, MP_set_all = mb.memory_cache_all_length(TS_newSet, MP_set_all, stack_size, inputTSBatch, m_list)
            shapList = sb.extract_shapelet_all_length(k, TS_newSet, MP_set_all, m_list)
            for shap in shapList:
                shap_set = [driftDetection.t_stamp, shap.name, shap.Class, str(shap.subseq), shap.normal_distance]
                shap_pd = pd.DataFrame([shap_set], columns=['t_stamp', 'shap.name', 'shap.Class', 'shap.subseq', 'shap.score'])
                output_shapelet = output_shapelet.append(shap_pd)

def blocking_task(dataset, window_size):
    '''global x, y
    while True:
        x += 1
        y = 2 ** x
        time.sleep(0.1)'''
    k = 10
    '''data_directory = "/Users/Jingwei/PycharmProjects/distributed_use/venv/TestDataset/UCR_TS_Archive_2015"
    datasetName = "/FordA/FordA_TRAIN"
    dataset = data_directory + datasetName'''
    m_ratio = 0.05
    stack_ratio = 0.01
    #window_size = 20
    global_structure(k, dataset, m_ratio, stack_ratio, window_size)

#Concept Drift Data: avg_loss, loss_batch, cum_loss, PH, t_stamp;
#Question: How to receive the information from GUI and react with it?
@account_api.route('/ConceptDrift/', methods=['POST'])
def data_ConceptDrft():
    global drift, loss_batch, avg_loss, t_stamp, thread, inputTSBatch, TS_set
    if drift == True:
        drift_num = 1
    else:
        #drift_num = float('nan')
        drift_num = -1

    list_inputTS = []
    list_TSset = []

    for inputTS in inputTSBatch:
        list_inputTS.append(str(inputTS.timeseries))
    for TS in TS_set:
        list_TSset.append(str(TS.timeseries))

    return jsonify(t_stamp=[t_stamp], drift_num=[drift_num], avg_loss=[avg_loss], loss_batch=[loss_batch], label_avg_loss = ['avg_loss'], label_loss_batch=['loss_TSmicroBatch'], label_concept_drift=['concept drift area'], inputTSBatch=[';'.join(list_inputTS)], TS_set=[';'.join(list_TSset)])

#TS data in new Window
#Question: How to read the window size and change the TS data shown in the GUI?
@account_api.route('/TSWindow/', methods=['POST'])
def data_TSWindow():
    global inputTSBatch, TS_set
    #How to return TS list data? -> as an object list?
    #print("inputTSBatch is: " + str(inputTSBatch))
    # Convert TS object to a serializable object (i.e. String)
    list_inputTS = []
    list_TSset = []

    for inputTS in inputTSBatch:
        list_inputTS.append(str(inputTS.timeseries))
    for TS in TS_set:
        list_TSset.append(str(TS.timeseries))
    return jsonify(inputTSBatch=[';'.join(list_inputTS)], TS_set=[';'.join(list_TSset)])


