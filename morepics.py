from __future__ import division
from matplotlib import pyplot  as plt
from matplotlib import cm
import sys
import numpy as np
import cPickle
from math import *

if __name__ == "__main__":
    quant = sys.argv[1]
    name = sys.argv[2]
    vals = eval(sys.argv[3])
    cps_x, cps_y, weight = [], [], []
    for i, val in enumerate(vals):
        fname = name + str(val)
        data = {}
        with open(fname + '.out') as f:
            data = cPickle.load(f)
            params = data['params']
            steps = 5000 
            trials = params['PROC'] * params['SIM'] 
            N = params['N']
            meets = params['MEETS']
            cps_x.extend([i] * trials * steps)
            weight.extend([1/(trials * steps)] * trials * steps)
            for j in xrange(trials):
                for k in xrange(steps):
                    cps_y.append(data['cps'][j][k] / meets)
    plt.figure()
    plt.xlabel(quant)
    plt.ylabel('Proportion of cooperations')
    plt.xticks(range(len(vals)), vals)
    plt.hexbin(cps_x, cps_y, weight, cmap=cm.binary, 
               gridsize=9, reduce_C_function=sum, vmin=0, vmax=1)        
    plt.colorbar()
    plt.savefig('data_cps.png', dpi=300)
