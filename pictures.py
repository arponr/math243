from __future__ import division
import matplotlib.pyplot as plt, sys
import cPickle
from math import *

if __name__ == "__main__":
    outname = sys.argv[1]
    fnames = sys.argv[2:]
    if len(fnames) == 0:
        fnames = [outname]
    results = {}
    for fname in fnames:
        with open(fname + '.out') as f:
            obj = cPickle.load(f)
            for (k, v) in obj.iteritems():
                if k == 'params':
                    v = [v] * v['PROC'] * v['SIM']
                if not k in results:
                    results[k] = []
                results[k].extend(v)
    n = len(results['ast'])
    w = int(ceil(sqrt(n)))
    h = int(ceil(n/w))
    plt.figure()
    for i in xrange(n):
        plt.subplot(w,h,i)
        plt.plot(results['ast'][i], 'b', label='avg. coop threshold')
        plt.plot(results['cps'][i] / results['params'][i]['MEETS'], 'r', label='num. cooperations')
        plt.plot(results['arp'][i], 'g', label='avg. reputation')
        #plt.plot(results['aft'][i], label='avg. fitness')
        plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    plt.savefig(outname + '.png',dpi=300)
    plt.show()

