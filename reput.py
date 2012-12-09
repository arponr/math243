from __future__ import division
import numpy as np
import numpy.random as nprand
import pylab
import random
import sys
import cPickle
from multiprocessing import Process, Queue

SEL = 1
# reset everyone's opinions of offspring
DIE_RESET = False

def wrand(weight):
    a = random.random() * weight.sum()
    for i, w in enumerate(weight):
        if a > w:
            a -= w
        else:
            return i

def normalise(A):
    for i in xrange(len(A)):
        A[:, i] /= max(A[:, i].sum(), 1)
    return A

def pagerank(A, alpha=.85, epsilon=1e-10):
    unif = np.ones(len(A)) / len(A)
    x = unif.copy()
    delta = epsilon + 1
    while delta > epsilon:
        y = alpha * np.dot(A, x) + (1 - alpha) * unif
        delta = abs(y - x).sum()
        x = y.copy()
    return x

def interact(fit, opi, rep, stg, n, c, b):
    cur = np.zeros(opi.shape)
    for t in xrange(n):
        don, rec = random.sample(xrange(len(rep)), 2)
        if rep[rec] > stg[don]:
            cur[don][rec] += 1
            fit[don] -= c*SEL
            fit[rec] += b*SEL
    opi = normalise((opi + cur) / 2)
    return fit, opi

def evolve(fit, opi, rep, stg, mu):
    pro = wrand(fit)
    die = random.randrange(len(fit))
    fit[die], rep[die] = fit[pro], rep[pro]
    if random.random() < mu:
        stg[die] = random.random()
    else:
        stg[die] = stg[pro]
    if DIE_RESET:
        opi[die] = 1
        opi[:,die] = 1
    else:
        opi[die] = opi[pro]
        opi[:, die] = opi[:, pro]
    opi = normalise(opi)
    return fit, opi, rep, stg

def run_on_proc(q, N, n, p):
    fit = np.ones(N)
    opi = np.identity(N)
    stg = nprand.rand(N)
    avg = []
    for t in xrange(n):
        if p * t % n == 0:
            print 'step', t
            avg.append(stg.sum() / N)
        rep = pagerank(opi)
        fit, opi = interact(fit, opi, rep, stg, 100, .1, .2)
        fit, opi, rep, stg = evolve(fit, opi, rep, stg, .001)
    q.put({'fit':fit, 'stg':stg, 'rep':rep, 'avg':avg})

def run(N, n, p, np = 1):
    q = Queue()
    for i in xrange(np):
        proc = Process(target=run_on_proc, args=(q, N, n, p))
        proc.start()
    arrs = {}
    for i in xrange(np):
        rets = q.get()
        for (k, ret) in rets.iteritems():
            if not k in arrs:
                arrs[k] = []
            arrs[k].append(ret)
    return arrs

if __name__ == "__main__":
    fname = sys.argv[1]
    if not fname.endswith('.out'):
        fname = fname + '.out'
    result = run(100, 100, 10000)
    with open(fname, 'w') as out:
        cPickle.dump(result, out)
