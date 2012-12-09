import matplotlib.pyplot as plt, sys
import cPickle

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
    for i in xrange(len(results['ast'])):
        plt.plot(results['ast'][i])
        plt.plot(results['arp'][i])
        plt.show()
    #plt.savefig(outname)
