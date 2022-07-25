# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 18:08:01 2021

@author: weeshinchew
"""


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Takes a pair of x,y values sorted by x in ascending order and returns
# kernel smoothed y samples with corresponding x. Number of samples is 
# influenced by n_order. If x is datetime information, set x_datetime=True
# and x_coordinates returned will be to datetime type
def fast_kernel_smooth(x, y, n_order=100, bandwidth=None, x_datetime=False):
    if x_datetime:
        x_time = x 
        x = pd.to_datetime(x) # assumes x can still be in string form
        x = (x - x.min()).dt.total_seconds()/(3600*24) # convert to days from earliest date
    
    
    if bandwidth is None:
        q75, q25 = np.percentile(x, [75 ,25])
        if np.isclose(q75, q25):
            iqr = 1    # set to unity when Q75 and Q25 are the same values which would lead to div by zero later on
        else:
            iqr = q75 - q25
        sigma = np.std(x)
        b = 1.06*min(sigma, iqr/1.34)*np.power(len(x),-0.2) # bandwidth
    else:
        b = bandwidth
    
    # Calculate the maximum length in which points contained within will be represented with just one point
    # This has the effect of priotizing sampling at sparse points (tail ends of distribution), and reduced sampling
    # at points with many 
    planck_length = (np.percentile(x, 90) - np.percentile(x, 10))/n_order
    cutoff = None
    x_collect = None
    n_collect = None # index to reference datetime string element when x is originally datetime
    
    # Reduced kernel smoothing points
    x_sampled = []
    y_sampled = []
    
    for n, (x_i,y_i) in enumerate(zip(x, y)):
        # Starting point
        if cutoff is None:
            cutoff = x_i + planck_length
            x_collect = x_i
            n_collect = n
        else:
            if x_i < cutoff: # Move on since this point is close to x_collect
                pass
            else:
                # Compute the kernel smoothed point at x_collect
                # and start new collection          
                scaled_dist = (x - x_collect*np.ones((x.shape[0],)))/b
                wgt = np.exp(-np.power(scaled_dist, 4))
                wgt = wgt/np.sum(wgt)
                
                if x_datetime:
                    x_sampled.append(x_time.iloc[n_collect])
                    y_sampled.append(np.dot(wgt, y))
                else:
                    x_sampled.append(x_collect)
                    y_sampled.append(np.dot(wgt, y))
                             
                x_collect = x_i
                n_collect = n
                cutoff = x_i + planck_length
                
    # Calculate last sample from leftover collection
    scaled_dist = (x - x_collect*np.ones((x.shape[0],)))/b
    wgt = np.exp(-np.power(scaled_dist, 4))
    wgt = wgt/np.sum(wgt)
    
    if x_datetime:
        x_sampled.append(x_time.iloc[n_collect])
        y_sampled.append(np.dot(wgt, y))
    else:
        x_sampled.append(x_collect)
        y_sampled.append(np.dot(wgt, y))
        
    # Convert x to datetime if needed
    if x_datetime:
        x_sampled = pd.to_datetime(x_sampled)
    
    return x_sampled, y_sampled

# Takes a pair of sorted x and y coordinates and returns the kernel smoothed y value
def kernel_smooth(x,y, bandwidth=None):
    x = np.array(x)
    y = np.array(y)
    
    n = len(x) # number of points
    
    # Debugging, to remove soon.
    if np.isnan(x).any():
        print('WARNING THERE ARE STILL EMPTY VALUES SOMEHOW')
    
    if bandwidth is None:
        q75, q25 = np.percentile(x, [75 ,25])
        if np.isclose(q75, q25):
            iqr = 1    # set to unity when Q75 and Q25 are the same values which would lead to div by zero later on
        else:
            iqr = q75 - q25
        sigma = np.std(x)
        b = 1.06*min(sigma, iqr/1.34)*np.power(len(x),-0.2) # bandwidth
    else:
        b = bandwidth
        
    ''' 2D matrix for weights. This will be a diagonal matrix. Consider the x 
     array to be:
    [a
     b
     c]
    
    then for each point, we calculate its distance from all other points:
    
    a a a     a b c    d_aa d_ab d_ac
    b b b   - a b c  = d_ba d_bb d_bc
    c c c     a b c    d_ca d_cb d_cc
    
    We scale the matrix by a factor 1/b where b is the bandwidth dependent on
    the x values, and feed it into a gaussian kernel exp(- input^4). Because
    the distance is raised to an even power, the matrix is now diagonal:
        
    W_aa W_ab W_ac    W_aa W_ab W_ac
    W_ba W_bb W_bc =  W_ab W_bb W_bc
    W_ca W_cb W_cc    W_ac W_bc W_cc
    
    W_ij physically represents the weight of the point i with reference to
    point j. Imagine if points a & b are close together while c is far away,
    such that d_aa = d_ab << d_ac. This means: W_aa ~ W_ab = 1, W_ac ~ 0. 
    
    We then normalize the weights by dividing by W_aa + W_ab + W_ac such 
    that the weight matrix resembles
    
    0.5 0.5 0.0
    0.5 0.5 0.0 
    0.0 0.0 1.0
    
    which we then use to matrix-multiply by the actual y values:
        
    0.5 0.5 0.0     y1    0.5*y1 + 0.5*y2
    0.5 0.5 0.0  x  y2  = 0.5*y1 + 0.5*y2
    0.0 0.0 1.0     y3    1*y3
    
    The resulting formula shows what kernel smoothing is doing: the smoothed 
    y-value of at a given x-value is calculated by a weighted average of the y-values 
    from points near the x-value. Because of the gaussian decay, points far
    away from the point to be smoothed have their weights very close to 0,
    allowing the value to only be affected by "nearby" measurements.
    
    Or in equation form,
    
    The smoothed value of a given point at x_0, is given by:
    Y_smooth(x_0) = SUM_i{ K( (x_0 - x_i)/b ) * y_i} / SUM_i{ K( (x_0 - x_i)/b )}
    
    where
    
    K(x) = exp(-x^4)
    and b is the formula shown previously.
    '''
    wgt = np.ones((n,n))
    
    wgt = (wgt*x).T
    ref = np.ones((n,n))*x
    
    # Calculate distances from all other points, then scale by bandwidth
    wgt = 1/b*(wgt - ref)
    # Calculate guassian kernels
    wgt = np.exp(-np.power(wgt,4))
    
    # Calculate sum of kernels to normalize weights
    kern_sum = np.sum(wgt, axis=1).reshape((n,1))
    wgt = wgt * 1/kern_sum
    
    y_smoothed = np.matmul(wgt, y)
    
    return y_smoothed


