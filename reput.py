from __future__ import division
import numpy as np
import numpy.random as nprand
import pylab
import random
import sys
import cPickle
from multiprocessing import Process, Queue

# selection strength
SEL = 1
# max pagerank-iterations
ITER = 10
# pagerank teleportation rate
ALPHA = 0.85
# interaction cost
C = .1
# interaction benefit
B = .2
# number of interactions per round
MEETS = 100
# mutation for strategy
MU_STG = .0001
# mutation for pagerank-iterations
MU_IND = .0001
# population size
N = 100
# number of rounds
STEPS = 50000
# how often to print progress
DUMP = 10
# number of threads
PROC = 4
# reset everyone's opinions of offspring
DIE_RESET = False
#Error rate in actions
ERR = 0

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

def pagerank(A):
    A = normalise(A)
    unif = np.ones(len(A)) / len(A)
    x = np.zeros((ITER+1, len(A)))
    x[0] = unif.copy()
    for i in xrange(ITER):
        x[i+1] = ALPHA * np.dot(A, x[i]) + (1 - ALPHA) * unif
    return x

def interact(fit, opi, rep, stg, ind):
    cur = np.zeros(opi.shape)
    coop = 0
    for t in xrange(MEETS):
        don, rec = random.sample(xrange(len(rep)), 2)
        if (rep[ind[don]][rec] > stg[don] and random.random() > ERR or
            rep[ind[don]][rec] < stg[don] and random.random() < ERR): 
            cur[don][rec] += 1
            fit[don] -= C * SEL
            fit[rec] += B * SEL
            coop += 1
    opi = (opi + cur) / 2
    return fit, opi, coop

def evolve(fit, opi, rep, stg, ind):
    pro = wrand(fit)
    die = random.randrange(len(fit))
    fit[die], rep[:, die] = fit[pro], rep[:, pro]
    if random.random() < MU_STG:
        stg[die] = random.random()
    else:
        stg[die] = stg[pro]
    if random.random() < MU_IND:
        ind[die] = random.randrange(ITER+1)
    else:
        ind[die] = ind[pro]
    opi[die] = opi[pro]
    opi[:,die] = opi[:,pro]
    if DIE_RESET:
        opi[die] = 1
        opi[:,die] = 1
    else:
        opi[die] = opi[pro]
        opi[:,die] = opi[:,pro]
    opi = normalise(opi)
    return fit, opi, rep, stg

def run_on_proc(q, pr):
    fit = np.ones(N)
    opi = np.identity(N)
    stg = nprand.rand(N)
    ind = nprand.random_integers(0, 10, N)
    avg = []
    for t in xrange(STEPS):
        if t % DUMP == 0:
            print 'proc %d: step %d' % (pr, t)
            avg.append(stg.sum() / N)
        rep = pagerank(opi)
        fit, opi = interact(fit, opi, rep, stg, ind)
        fit, opi, rep, stg = evolve(fit, opi, rep, stg, ind)
    q.put({'fit':fit, 'stg':stg, 'ind':ind, 'rep':rep, 'avg':avg})

def run():
    q = Queue()
    for i in xrange(PROC):
        proc = Process(target=run_on_proc, args=(q, i))
        proc.start()
    arrs = {}
    for i in xrange(PROC):
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
    result = run()
    with open(fname, 'w') as out:
        cPickle.dump(result, out)
