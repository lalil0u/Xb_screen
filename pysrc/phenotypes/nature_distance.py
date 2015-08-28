import os, sys, re, time

import numpy as np

import cellh5
import pdb

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import statsmodels.api as sm
import pickle

TEST_FOLDER = '/Users/twalter/data/Alice/trajectory_distance_test/plots'


class TimeSeriesPositionReader(object):
    def __init__(self, filename, channel='primary__test'):
        self.filename = filename
        self.channel = channel
        
    def __call__(self):
                
        cm = cellh5.CH5MappedFile(self.filename)
        try:
            pos = cm.current_pos 
                
            if len(pos['object'][self.channel]) == 0:
                cm.close()
                return
    
            objects = pos.get_object_table(self.channel)
            frames_of_objects = np.array([x[0] for x in objects])
            predictions = np.array([x[0] for x in pos.get_class_prediction(self.channel)])
            names = pos.definitions.class_definition(self.channel)['name']
    
            time_indices = range(np.max(frames_of_objects))
            class_indices = range(len(names))
            
            # prediction_counts is a matrix with class counts as columns
            # and frames as rows.        
            prediction_counts = np.array([np.bincount(predictions[frames_of_objects==t], 
                                                      minlength=len(names)) 
                                          for t in time_indices])
    
            # the full cell counts (in the right dimension for row normalization)
            counts = prediction_counts.sum(axis=1, keepdims=True)
            
            # if the total number of cells is 0, we can set it to 1 (the percentages are 0 anyway)
            counts[counts==0] = 1

            # normalization (percentages for each time point)
            # each row is divided by the cell count. 
            X = prediction_counts.astype(np.float) / counts

        except:
            print 'PROBLEM: filename = ', self.filename
            print 'SKIPPING ... '
            cm.close()
            return None
        
        cm.close()
        return X
    
class TwoVectorRepresentation(object):
    
    def __init__(self):
        self.test_folder = TEST_FOLDER
    
    def dist(self, x, y):   
        return np.sqrt(np.sum((x-y)**2))

    def squared_dist(self, x, y):   
        return np.sum((x-y)**2)

    def squared_norm(self, x):   
        return np.sum(x**2)

    def norm(self, x):   
        return np.sqrt(np.sum(x**2))
    
    def get_lse(self, X, middle_index):
        
        xinit = X[0]
        xend = X[X.shape[0]-1]
        m = X[middle_index]
        a = m - xinit
        b = xend - m 

        a_snorm = self.squared_norm(a)
        b_snorm = self.squared_norm(b)
                
        res = 0.0
        if a_snorm > 0:
            for j in range(1, middle_index):
                x_j = X[j] - xinit
                k = np.dot(x_j, a)            
                res += self.squared_norm(x_j) - k * k / a_snorm
                                
                
        if b_snorm > 0:            
            if middle_index in [55, 62]:
                print
            for j in range(middle_index + 1, X.shape[0]):
                x_j = X[j] - m
                k = np.dot(x_j, b)
                res += self.squared_norm(x_j) - k * k / b_snorm

        return res
    
    def __call__(self, X, col_indices=None):
        nb_frames = X.shape[0]

        if not col_indices is None:
            Xsub = X[:,col_indices]
        else:
            Xsub = X
                    
        # initialization
        lse = self.get_lse(Xsub, 1)
        index = 1
        
        for middle_index in range(2, nb_frames - 1):
            lse_current = self.get_lse(Xsub, middle_index)
            if lse_current < lse:
                lse = lse_current
                index = middle_index
            
        a = Xsub[index] - Xsub[0]
        b = Xsub[-1] - Xsub[index]
        return a, b, index, lse
 
    def smooth_counts(self, X):
        # lowess
        lowess = sm.nonparametric.lowess
        Xsmooth = X.copy()
        
        for j in range(X.shape[1]):
            Xsmooth[:,j] = np.array([x[1] for x in 
                                     lowess(X[:,j], range(X.shape[0]), frac=0.5)])
            
        return Xsmooth
    
    def test_plot(self, X, col_indices=None):
        if col_indices is None:
            col_indices = np.array([3, 4])

        Xs = self.smooth_counts(X)            
        a, b, mi, lse = self.__call__(Xs, col_indices)
        
        print 'index: ', mi, 'lse: ', lse
        
        index = len(os.listdir(self.test_folder))
        filename = os.path.join(self.test_folder, 'twovec_test_%03i.png' % index)
        
        fig = plt.figure(1)
        ax = plt.subplot(1,1,1)
        
        xs1 = Xs[:,col_indices[0]]
        xs2 = Xs[:,col_indices[1]]
        
        c1 = plt.Circle((xs1[mi], xs2[mi]), 0.0005, color='green', fill=False)
        plt.plot(xs1, xs2, 'ro')
        fig.gca().add_artist(c1)

        plt.plot([xs1[0], xs1[mi]], [xs2[0], xs2[mi]], color='orange', linestyle='-', linewidth=2)
        plt.plot([xs1[-1], xs1[mi]], [xs2[-1], xs2[mi]], color='orange', linestyle='-', linewidth=2)
        
        minval = np.min(Xs[:,col_indices])
        maxval = np.max(Xs[:, col_indices])
        
        axis = [minval - (maxval-minval)*0.05,
                maxval + (maxval-minval) * 0.05,
                minval - (maxval-minval)*0.05,
                maxval + (maxval-minval) * 0.05]
        
        plt.axis(axis)
        ax.set_aspect('equal')

        plt.savefig(filename)
        plt.close(1)

        return
    
    
class TrajectoryDistance(object):
    
    def __init__(self, col_indices=None, exclude_interphase = True, smooth=True, 
                 beta=0.5,
                 channel = 'primary__test'):
	'''
- col_indices: if you wish to specify precisely which columns for the distance computation
- smooth: to do smoothing of phenotypic time series (keep to True)
'''
        
        self.col_indices = col_indices
        self.exclude_interphase = exclude_interphase
        self.smooth = smooth
        self.tvr = TwoVectorRepresentation()        
        self.beta = beta
        self.channel = channel
        return
    
    def angle_difference(self, v1, v2):
        l1 = self.tvr.norm(v1)
        l2 = self.tvr.norm(v2)
        min_len = min(l1, l2)
        if min_len == 0:
            res = 0.0
        else:
            res = 2.0 * min_len * np.sin(.5 * np.arccos(np.dot(l1, l2) / (l1 * l2)) )

        return res
    
    
    def calc_dist_2_matrices(self, X1, X2):
        
        if self.smooth:
            X1s = self.tvr.smooth_counts(X1)
            X2s = self.tvr.smooth_counts(X2)
        else:
            X1s = X1
            X2s = X2
        
        if not self.col_indices is None:
            X1s = X1s[:, self.col_indices]
            X2s = X2s[:, self.col_indices]
        else:
            if self.exclude_interphase:
                X1s = X1s[:,1:X1s.shape[1]]
                X2s = X2s[:,1:X2s.shape[1]]
        
        a1, b1, mi1, lse1 = self.tvr(X1s)
        a2, b2, mi2, lse2 = self.tvr(X2s)
        
        mv1 = X1s[mi1]
        mv2 = X2s[mi2]
        
        # euclidean distance between start, middle and end points
        dist = self.tvr.dist(X1s[0], X2s[0]) + \
               self.tvr.dist(mv1, mv2) + \
               self.tvr.dist(X1s[-1], X2s[-1])
        
        # angle distances
        dist += self.beta * (self.angle_difference(a1, a2) + self.angle_difference(b1, b2))
                
        return dist
        
    def __call__(self, A, B):
        if type(A) is str:
            tspr = TimeSeriesPositionReader(A, channel=self.channel)
            X1 = tspr()
        else:
            X1 = A
            
        if type(B) is str:
            tspr = TimeSeriesPositionReader(B, channel=self.channel)
            X2 = tspr()
        else:
            X2 = B    
        
        dist = self.calc_dist_2_matrices(X1, X2)
            
        return dist
    
    
def batchtest():
    in_folder = '/Users/twalter/data/Alice/trajectory_distance_test/some_tests/check'

    filenames = filter(lambda x: x.split('.')[-1] == 'ch5', os.listdir(in_folder))
    title = ['poly', 'binuclear', 'mito', 'binuclear', 'mito', 'poly', 'mito']

    pickle_filename = os.path.join(in_folder, 'matrices.pickle')
    if os.path.isfile(pickle_filename):
        fp = open(os.path.join(in_folder, 'matrices.pickle'), 'r')
        reading = pickle.load(fp)
        fp.close()
    else:
        reading = []    
        for filename in filenames:
            tspr = TimeSeriesPositionReader(os.path.join(in_folder, filename))
            reading.append(tspr())
        
        fp = open(os.path.join(in_folder, 'matrices.pickle'), 'w')
        pickle.dump(reading, fp)
        fp.close()
    
    dist = TrajectoryDistance()
    for i in range(len(filenames) - 1):
        for j in range(i+1, len(filenames)):
            val = dist(reading[i], reading[j])
            print '%s vs %s: %f' % (filenames[i], filenames[j], val)
            print '%s vs %s: %f' % (title[i], title[j], val)
            print
            
            
        
        
    