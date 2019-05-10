import numpy as np
import similarity_measures as sm
import SMAP.MatrixProfile as mp
import memory_block as mb
import utils.utils as util
import time

def discm_profile(TS_set, MP_set, m):
    #Exponential Moving Average (EMA), but the number of instances in each class is different.
    #Simple Moving Average (SMA) is implemented here
    mp_dict_same = []
    mp_dict_differ = []
    TS_set_new=[]
    # mp_dict_same: [mp1, mp2, ...], Array[Array[]]
    # mp_all: {ts_target.name1:mp1, ts_target.name2:mp2, ...}, dict(ts_targe.name:Array[])
    # dp_all: {ts_target.name1:{index1:dp1, index2:dp2, ...}, ts_target.name2:{...}, ...}, dict(ts_target.name: dict(index:Array[]) )
    for idx_s, ts_source in enumerate(TS_set):
        for idx_t, ts_target in enumerate(TS_set):
            if idx_s == idx_t:
                continue
            #print("idx_s:idx_t is " + str(idx_s) + ":" + str(idx_t))
            if ts_source.class_timeseries == ts_target.class_timeseries:
                mp_sameClass = MP_set[idx_s][idx_t]
                mp_dict_same.append(mp_sameClass)
            else:
                mp_differClass = MP_set[idx_s][idx_t]
                mp_dict_differ.append(mp_differClass)

            #print("ts is " + str(ts_source.timeseries))
            #print("mp_differClass is " + str(MP_set[idx_s][idx_t]) + "class_s is " + str(ts_source.class_timeseries) + "class_t is " + str(ts_target.class_timeseries))
        # compute the average distance for each side (under the same class, or the different class)
        dist_intraC = np.mean(mp_dict_same, axis=0)
        dist_interC = np.mean(mp_dict_differ, axis=0)
        #print("dist_interc is: " +str(dist_interC))

        # compute the difference of distance for 2 sides
        ts_source.discmP.update({m:np.subtract(dist_interC, dist_intraC)})
        ts_source.threshP.update({m:dist_intraC})
        TS_set_new.append(ts_source)
    return TS_set_new

def extract_shapelet(k, TS_set, MP_set, m):
    DiscmPList_dic = {}
    ThreshList_dict = {}
    class_list = []
    shapelet_list = []
    TS_set = discm_profile(TS_set, MP_set, m)
    for ts in TS_set:
        c = ts.class_timeseries
        class_list.append(c)
        if c in DiscmPList_dic.keys():
            DiscmPList_dic[c].update({ts.name: ts.discmP[m]})
            ThreshList_dict[c].update({ts.name: ts.threshP[m]})
        else:
            DiscmPList_dic[c] = {ts.name: ts.discmP[m]}
            ThreshList_dict[c] = {ts.name: ts.threshP[m]}
        # for each class, select top-k shapelets, then find the matching indices for top-k shapelets
        # top-k aims at the shapelets of different class, or top-k shapelets of each class?
        ## Here, we take k shapelets for each class
        ### remove repetitive element in class_list
    class_list = list(set(class_list))
    for c in class_list:
        ts_namelist = DiscmPList_dic[c].keys()
        # take the k first values as the initial values, then update them
        keys = range(0, k)
        # take top k shapelets for each class
        topk_discmPower = dict.fromkeys(keys, float('-inf'))
        for ts in ts_namelist:
            ## Discm. Profile of source timeseries 'ts'
            dp = DiscmPList_dic[c][ts]
            #print("class c is " + str(c) + "DiscmProfile is " + str(dp))
            # 'idx' is the position of max difference of distance for 'ts'
            for idx, DiscmPower in enumerate(dp):
                # if we find an element in 'topk_distdiff' which is smaller than 'dd',
                # then remove it and add 'dd' into 'topk', then break
                min_topk = min(topk_discmPower.values())
                for idx_topk, dd_topk in topk_discmPower.items():
                    if dd_topk == min_topk and dd_topk < DiscmPower:
                        topk_discmPower.pop(idx_topk)
                        key_composed = str(ts) + "_" + str(idx)
                        topk_discmPower.update({key_composed: DiscmPower})
                        break
        # create shapelets and put matching timeseries
        # topk_discmPower: {ts_name_source+index1 : DiscmPower1, ts_name_source+index2 : DiscmPower2, ... }
        #print(topk_discmPower.values())
        for key, val in topk_discmPower.items():
            if type(key) != int:
                key_val = key.split("_")
                ts_name_source = int(key_val[0])
                # the position of the shapelet in the source timeseries
                ts_index_source = int(key_val[1])

                shap = util.Shapelet()
                shap.Class = c
                shap.differ_distance = val
                shap.normal_distance = val / (m ** 0.5)
                s = [ts for ts in TS_set if ts.name==ts_name_source][0]
                #to decide the value of Shapelet, back to the off-set in original TS
                if int(m / 4) == 0:
                    step = 1
                else:
                    step = int(m / 4)
                idx_in_rawTS = ts_index_source * step
                shap.subseq = s.timeseries[idx_in_rawTS:idx_in_rawTS + m]
                # hashing the raw data of subsequence as shapelet name
                shap.name = hash(shap.subseq.tostring())

                # 'dist_threshold_list[c]': {ts_name_source1:dist_threshold1, ts_name_source2:dist_threshold2, ...}, dict(String:Array[])
                dist_thd = ThreshList_dict[c][ts_name_source][ts_index_source]
                shap.dist_threshold = dist_thd
                shapelet_list.append(shap)
            else:
                print("key is " + str(key))
    # for each class, we've token k shapelets, so the final result contains k * nbr(class) shapelets
    return shapelet_list

def update_shaplet(k, inputTSBatch, TS_set, MP_set, m):
    #Consider Forgetting Mechanism in Streaming case
    TS_set, MP_set = mb.memory_cache(TS_set, MP_set, inputTSBatch, m)
    newShapList = extract_shapelet(k, TS_set, MP_set, m)
    return newShapList

def extract_shapelet_all_length(k, TS_set, MP_set, m_step):
    #'TS_set': [dict{}, dict{}, ...]
    min_m = util.min_length_dataset(TS_set)
    shap_list = []
    for m in m_step:
        #print("Extracting shapelet length: " + str(m))
        start = time.time()
        #number of shapelet in shap_list: k * nbr_class * (min_l-1)
        nbr_candidate = int((min_m - m)/(0.25*m))
        if 0 < nbr_candidate < k :
            shap_list.extend(extract_shapelet(k, TS_set, MP_set[m], m))
        elif nbr_candidate > 0:
            shap_list.extend(extract_shapelet(k, TS_set, MP_set[m], m))
        #print("time consumed: ", str(time.time() - start))
    # for each TS class, extract k shapelets
    grouped_shapelets = {}
    list_all_shapelets_pruned = []
    for shap in shap_list:
        if shap.Class in grouped_shapelets.keys():
            grouped_shapelets[shap.Class].append(shap)
        else:
            grouped_shapelets[shap.Class] = [shap]
    for keyShapelet, groupShapelet in grouped_shapelets.items():
        list_shapelet_group = list(groupShapelet)
        shap_list_sorted = sorted(list_shapelet_group, key=lambda shap: shap.normal_distance, reverse=True)
        list_all_shapelets_pruned += shap_list_sorted[:int(k)]
    return list_all_shapelets_pruned
