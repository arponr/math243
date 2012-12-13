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
    vary = sys.argv[3]
    stg_x, stg_y = [], []
    rep_x, rep_y = [], []
    fit_x, fit_y = [], []
    weight = []
    for i, val in enumerate(vals):
        fname = name + str(val)
        data = {}
        with open(fname + '.out') as f:
            data = cPickle.load(f)
            params = data['params']
            snaps = int(params['STEPS'] / params['DUMP'])
            trials = params['PROC'] * params['SIM'] 
            N = params['N']
            for k in xrange(snaps):
                if i == 0:
                    stg_x.append([])
                    rep_x.append([])
                    fit_x.append([])
                    stg_y.append([])
                    rep_y.append([])
                    fit_y.append([])
                    weight.append([])
                stg_x[k].extend([i] * trials * N)
                rep_x[k].extend([i] * trials * N)
                fit_x[k].extend([i] * trials * N)
                if vary == 0:
                    weight.extend([1] * trials * N)
                else:
                    weight.extend([1/N] * trials * N)
                for j in xrange(trials):
                    stg_y[k].extend(data['pst'][j][k])
                    rep_y[k].extend(data['prp'][j][k])
                    fit_y[k].extend(data['pft'][j][k])
    for k in xrange(1, snaps):
        plt.figure()
        plt.hexbin(rep_x[k], rep_y[k], weights[k], cmap=cm.binary, 
                   gridsize=10, reduce_C_function=sum)
        plt.savefig('data%d.png' % k, dpi=300)
