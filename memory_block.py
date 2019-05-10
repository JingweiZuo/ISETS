import numpy as np
import similarity_measures as sm
import SMAP.MatrixProfile as mp

# centralized & distributed algorithm
def TS_cache(TS_set, stack_size, inputTSBatch):
    #cache TS batches
    w = len(inputTSBatch)
    if len(TS_set) > stack_size:
        TS_set = TS_set[w:]
    TS_set = np.concatenate([TS_set,inputTSBatch])
    return TS_set

def MP_cache(TS_set, MP_set, stack_size, inputTSBatch, m):
    #cache Matrix Profile
    i = 0
    j = 0
    w = len(inputTSBatch)
    if len(TS_set) == 0:
        MP_set = np.empty((w, w),dtype=object)
        for ts_source in inputTSBatch:
            for ts_target in inputTSBatch:
                if ts_source!=ts_target :
                    MP_set[i][j] = mp.computeMP(ts_source, ts_target, m)
                    #print(ts_target)
                j += 1
            i += 1
            j = 0
        #print(MP_set)
    else:
        row = np.empty((w, len(TS_set)),dtype=object)
        col = np.empty((w, len(TS_set)+w),dtype=object)
        MP_set = np.insert(MP_set, len(MP_set), row, axis=0)
        MP_set = np.insert(MP_set, len(MP_set[1]), col, axis=1)
        for ts_old in TS_set.extend(inputTSBatch):
            for ts_new in inputTSBatch:
                if ts_old != ts_new :
                    ##########################to complete the commun part##########################
                    MP_set[i][len(TS_set)+j] = mp.computeMP(ts_old, ts_new, m)
                    MP_set[len(TS_set)+j][i] = mp.computeMP(ts_new, ts_old, m)
                    j += 1
            i += 1
            j = 0
    if len(MP_set) > stack_size:
        MP_set = MP_set[w:][w:]
    return MP_set

def memory_cache_all_length(TS_set, MP_set_all, stack_size, inputTSBatch, m_list):
    for m in m_list:
        MP_set_all.update({m: MP_cache(TS_set, MP_set_all, stack_size, inputTSBatch, m)})
    TS_newSet = TS_cache(TS_set, stack_size, inputTSBatch)
    return TS_newSet, MP_set_all

