from __future__ import division
import matplotlib.pyplot as plt, sys
import cPickle
from math import *

if __name__ == "__main__":
    outname = sys.argv[1]
    fnames = sys.argv[2:]
    results = {}
    for fname in fnames:
        with open(fname) as f:
            obj = cPickle.load(f)
            for (k, v) in obj.iteritems():
                if not k in results:
                    results[k] = []
                results[k].extend(v)
    n = len(results['ast'])
    w = int(ceil(sqrt(n)))
    h = int(ceil(n/w))
    for i in xrange(n):
        plt.subplot(w,h,i)
        plt.plot(results['ast'][i], label='avg. coop threshold')
        plt.plot(results['arp'][i], label='avg. reputation')
        plt.plot(results['aft'][i], label='avg. fitness')
        plt.legend()
    plt.savefig(outname,dpi=300)
    plt.show()

