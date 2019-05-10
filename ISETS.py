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
    global drift
    min_m = util.min_length_dataset(dataset_list)
    print("Maximum length of shapelet is : " + str(min_m))
    min_length = int(0.1 * min_m)
    max_length = int(0.5 * min_m)
    m_list =range(min_length, max_length, int(min_m * m_ratio))
    stack_size = stack_ratio * len(dataset_list)
    TS_set = []
    MP_set_all = {}

    #Initialization of shapList
    driftDetection = eb.driftDetection()
    inputTSBatch = driftDetection.stream_window(dataset_list, window_size)
    TS_newSet, MP_set_all = mb.memory_cache_all_length(TS_set, MP_set_all, stack_size, inputTSBatch, m_list)
    print(len(TS_newSet))

    shapList = sb.extract_shapelet_all_length(k, TS_newSet, MP_set_all, m_list)
    output_loss = pd.DataFrame([[0,0,0,0,0,0]], columns=['t_stamp', 'loss_batch', 'cum_loss', 'PH', 'avg_loss', 'nbr_drift'])
    output_shapelet = pd.DataFrame([[0,0,0,0,0]], columns=['t_stamp', 'shap.name', 'shap.Class', 'shap.subseq', 'shap.score'])
    while driftDetection.t_stamp < len(dataset_list):
        inputTSBatch = driftDetection.stream_window(dataset_list, window_size)
        drift, loss_batch, cum_loss, PH, avg_loss = driftDetection.shapelet_matching(shapList, inputTSBatch)
        if drift == True:
            nbr_drift = 1
        else:
            nbr_drift = 0
        loss_set = [driftDetection.t_stamp, loss_batch, cum_loss, PH, avg_loss, nbr_drift]
        loss_pd = pd.DataFrame([loss_set],
                                   columns=['t_stamp', 'loss_batch', 'cum_loss', 'PH', 'avg_loss', 'nbr_drift'])
        output_loss = output_loss.append(loss_pd)

        print("Drift is " + str(drift))
        if drift == True:
            TS_newSet, MP_set_all = mb.memory_cache_all_length(TS_set, MP_set_all, stack_size, inputTSBatch, m_list)
            shapList = sb.extract_shapelet_all_length(k, TS_newSet, MP_set_all, m_list)
            for shap in shapList:
                shap_set = [driftDetection.t_stamp, shap.name, shap.Class, str(shap.subseq), shap.normal_distance]
                shap_pd = pd.DataFrame([shap_set], columns=['t_stamp', 'shap.name', 'shap.Class', 'shap.subseq', 'shap.score'])
                output_shapelet = output_shapelet.append(shap_pd)
    output_loss.to_csv("output_loss2.csv", index=False)
    output_shapelet.to_csv("output_shapelet2.csv", index=False)

if __name__ == "__main__":
    k = 10
    data_directory = "/Users/Jingwei/PycharmProjects/distributed_use/venv/TestDataset/UCR_TS_Archive_2015"
    datasetName = "/FordA/FordA_TRAIN"
    dataset = data_directory + datasetName
    m_ratio = 0.05
    stack_ratio = 1
    window_size = 20
    global_structure(k, dataset, m_ratio, stack_ratio, window_size)

