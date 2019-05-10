import numpy as np
import similarity_measures as sm
import utils.utils as util

class driftDetection(object):
    def __init__(self):
        self.n_batch = 0
        self.t_stamp = 0
        self.avg_loss = 0
        self.cum_loss = 0
        self.mincum_loss = np.inf
        # Parameters to set
        self.tolerance = 0  # The loss tolerance for PH test
        self.thresh = 0  # Threshold of concept drift for PH test
        self.theta = 1  # The slope of Sigmoid Function

    #sigmoid = lambda x: 1 / (1 + np.exp(-x))
    def sigmoid(self, x, theta, x0):
        return (1 / (1 + np.exp(-theta*(x-x0))))

    def shapelet_matching(self, shap_set, TS_window):
        # using Sigmoid for Loss Function
        # parallel computing for TSs in the window
        drift = True
        loss_batch = 0
        w = len(TS_window)
        # Loss Computing, with a fading strategy or not?
        for ts in TS_window:
            shap_set_part = [s for s in shap_set if s.Class == ts.class_timeseries]
            min_dist = np.inf
            min_s = util.Shapelet()
            # find the closest Shapelet to 'ts'
            for s in shap_set_part:
                dist = np.min(sm.calculate_distances(ts.timeseries, s.subseq, "mass_v2"))
                if min_dist > dist:
                    min_dist = dist
                    min_s = s

            l = self.sigmoid(min_dist, self.theta, min_s.dist_threshold)
            loss_batch += l
        loss_batch = loss_batch / w
        self.n_batch += 1
        self.avg_loss = self.avg_loss*(self.n_batch-1)/self.n_batch + loss_batch/self.n_batch
        self.cum_loss = self.cum_loss + loss_batch - self.avg_loss - self.tolerance
        PH = self.cum_loss - self.mincum_loss
        if self.n_batch == 1:
            self.cum_loss = self.avg_loss
        if PH < 0:
            self.mincum_loss = self.cum_loss
        # Check if there's a Concept Drift
        '''if PH >= self.thresh:
            drift = True
        else:
            drift = False'''
        if self.avg_loss <= loss_batch:
            drift = True
        else:
            drift = False
        print("PH is: " + str(PH))
        print("loss_batch is: " + str(loss_batch))
        print("self.avg_loss is: " + str(self.avg_loss))
        print("self.cum_loss is: " + str(self.cum_loss))
        return drift, loss_batch, self.cum_loss, PH, self.avg_loss

    def stream_window(self, dataset, window_size):
        w = dataset[self.t_stamp:self.t_stamp+window_size]
        self.t_stamp += window_size
        return w

