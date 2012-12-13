from __future__ import division
import matplotlib.pyplot as plt, sys
import numpy as np
import cPickle
from math import *

if __name__ == "__main__":
    name = sys.argv[1]
    vals = eval(sys.argv[2])
    stg_x, stg_y = [], []
    rep_x, rep_y = [], []
    fit_x, fit_y = [], []
    for i, val in enumerate(vals):
        fname = name + str(val)
        data = {}
        with open(fname + '.out') as f:
            data = cPickle.load(f)
            params = data['params']
            snaps = int(params['STEPS'] / params['DUMP'])
            PROC = params['PROC']
            SIM = params['SIM'] 
            N = params['N']
            for k in xrange(snaps):
                if i == 0:
                    stg_x.append([])
                    rep_x.append([])
                    fit_x.append([])
                    stg_y.append([])
                    rep_y.append([])
                    fit_y.append([])
                stg_x[k].extend([i] * PROC * SIM * N)
                rep_x[k].extend([i] * PROC * SIM * N)
                fit_x[k].extend([i] * PROC * SIM * N)
                for j in xrange(PROC * SIM):
                    stg_y[k].extend(data['pst'][j][k])
                    rep_y[k].extend(data['prp'][j][k])
                    fit_y[k].extend(data['pft'][j][k])
    for k in xrange(snaps):
        plt.figure()
        plt.plot(stg_x[k], stg_y[k], 'ro', alpha=0.5)
    plt.show()
