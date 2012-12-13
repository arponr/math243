from __future__ import division
from matplotlib import pyplot  as plt
from matplotlib import cm
import sys
import numpy as np
import cPickle
from math import *

if __name__ == "__main__":
    name = sys.argv[1]
    vals = eval(sys.argv[2])
    vary = int(sys.argv[3])
    stg_x, stg_y = [], []
    rep_x, rep_y = [], []
    fit_x, fit_y = [], []
    cps_x, cps_y = [], []
    weight = []
    for i, val in enumerate(vals):
        fname = name + str(val)
        data = {}
        with open(fname + '.out') as f:
            data = cPickle.load(f)
            params = data['params']
            dump = params['DUMP']
            snaps = int(params['STEPS'] / params['DUMP'])
            trials = params['PROC'] * params['SIM'] 
            N = params['N']
            meets = params['MEETS']
            for k in xrange(snaps):
                if i == 0:
                    stg_x.append([])
                    rep_x.append([])
                    fit_x.append([])
                    cps_x.append([])
                    stg_y.append([])
                    rep_y.append([])
                    fit_y.append([])
                    cps_y.append([])
                    weight.append([])
                stg_x[k].extend([i] * trials * N)
                rep_x[k].extend([i] * trials * N)
                fit_x[k].extend([i] * trials * N)
                cps_x[k].extend([i] * trials)
                if vary == 0:
                    weight[k].extend([1/trials] * trials * N)
                else:
                    weight[k].extend([1/trials] * trials * N)
                for j in xrange(trials):
                    stg_y[k].extend(data['pst'][j][k])
                    rep_y[k].extend(data['prp'][j][k])
                    fit_y[k].extend(data['pft'][j][k])
                    cps_y[k].append(data['cps'][j][k * dump] / meets)
    for k in xrange(1, snaps):
        plt.figure()
        plt.hexbin(cps_x[k], cps_y[k], weight[k], cmap=cm.binary, 
                   gridsize=10, reduce_C_function=sum)        
        plt.colorbar()
        plt.savefig('data_%d_%d.png' % (vary, k), dpi=300)
