import numpy as np
import similarity_measures as sm
import SMAP.MatrixProfile as mp

# centralized & distributed algorithm
def TS_cache(TS_set, stack_size, inputTSBatch):
    #cache TS batches
    w = len(inputTSBatch)
    TS_set.extend(inputTSBatch)
    if len(TS_set) > stack_size:
        TS_set_new = TS_set[-stack_size:].copy()
        return TS_set_new
    return TS_set


def MP_cache(TS_set_input, MP_set, stack_size, inputTSBatch, m):
    #cache Matrix Profile
    i = 0
    j = 0
    w = len(inputTSBatch)
    TS_set = TS_set_input.copy()
    if len(TS_set) == 0:
        MP_set = np.empty((w, w),dtype=object)
        for ts_source in inputTSBatch:
            for ts_target in inputTSBatch:
                if ts_source!=ts_target :
                    MP_set[i][j] = mp.computeMP(ts_source, ts_target, m)
                j += 1
            i += 1
            j = 0
    else:
        row = np.empty((w, len(MP_set)),dtype=object)
        col = np.empty((w, len(MP_set)+w),dtype=object)
        print("row.shape is " + str(row.shape))
        print("col.shape is " + str(col.shape))

        MP_set = np.insert(MP_set, len(MP_set), row, axis=0)
        MP_set = np.insert(MP_set, len(MP_set[1]), col, axis=1)
        TS_set_old = TS_set.copy()
        TS_set.extend(inputTSBatch)
        print("size(TS_set) : " + str(len(TS_set_old)))
        print("MP_set.shape is " + str(MP_set.shape))
        for ts_old in TS_set:
            for ts_new in inputTSBatch:
                if ts_old != ts_new :
                    ##########################to complete the commun part##########################
                    #print("len(TS_set_old)+j: " + str(len(TS_set_old) + j) + "i:" + str(i))
                    MP_set[i][len(TS_set_old)+j] = mp.computeMP(ts_old, ts_new, m)
                    MP_set[len(TS_set_old)+j][i] = mp.computeMP(ts_new, ts_old, m)

                j += 1
            i += 1
            j = 0
    if len(MP_set[1]) > stack_size:
        MP_set = MP_set[-stack_size:,-stack_size:]
        print("if len(MP_set) > stack_size: " + str(MP_set.shape))
    return MP_set

def memory_cache_all_length(TS_set, MP_set_all, stack_size, inputTSBatch, m_list):
    for m in m_list:
        if m not in MP_set_all.keys():
            w = len(inputTSBatch)
            MP_set = np.empty((w, w), dtype=object)
            MP_set_all.update({m: MP_cache(TS_set, MP_set, stack_size, inputTSBatch, m)})
        else:
            print("size(TS_set) : " + str(len(TS_set)))
            MP_set_all.update({m: MP_cache(TS_set, MP_set_all[m], stack_size, inputTSBatch, m)})
    TS_newSet = TS_cache(TS_set, stack_size, inputTSBatch)
    return TS_newSet, MP_set_all

