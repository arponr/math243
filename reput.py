from __future__ import division
import numpy as np
import numpy.random as nprand
import pylab
import random
import sys
import cPickle
from multiprocessing import Process, Queue

# selection strength
SEL = .1
# max pagerank-iterations
ITER = 10
# pagerank non-teleportation rate
ALPHA = 0.85
# interaction cost
C = 1
# interaction benefit
B = 1.1
# number of interactions per round
MEETS = 500
# mutation probability for strategy
MU_STG = .0001
# mutation probability for pagerank-iterations
MU_IND = 0 #MU_IND = .0001
# population size
N = 100
# number of rounds
STEPS = 10000
# how often to print progress
DUMP = 10
# number of threads
PROC = 1
# reset everyone's opinions of offspring
DIE_RESET = False
# error rate in actions
ERR = 0
# true: interact round-robin; false: interact randomly
ROBIN = False
# true: remember the past (with discounting); false: don't
MEMORY = False

def wrand(weight):
    a = random.random() * weight.sum()
    for i, w in enumerate(weight):
        if a > w:
            a -= w
        else:
            return i

def normalise(A):
    return A / A.sum(1)

def pagerank(A):
    B = normalise(A)
    unif = np.ones(len(B)) / len(B)
    x = np.zeros((ITER+1, len(B)))
    x[0] = unif.copy()
    for i in xrange(ITER):
        x[i+1] = ALPHA * np.dot(B, x[i]) + (1 - ALPHA) * unif
    return x

def interact(fit, opi, rep, stg, ind):
    def interact_one(don, rec):
        new = 0
        if (rep[ind[don]][rec] > stg[don] and random.random() > ERR or
            rep[ind[don]][rec] < stg[don] and random.random() < ERR):
            new = 1
            fit[don] -= C * SEL
            fit[rec] += B * SEL
        if MEMORY:
            opi[don][rec] = (opi[don][rec] + new/2) / 2
        else:
            opi[don][rec] = new
    if ROBIN:
        for don in xrange(N):
            for rec in xrange(N):
                if don == rec:
                    continue
                interact_one(don, rec)
    else:
        for t in xrange(MEETS):
            don, rec = random.sample(xrange(N), 2)
            interact_one(don, rec)
    return fit, opi

def evolve(fit, opi, rep, stg, ind):
    pro = wrand(fit)
    die = random.randrange(N)
    fit[die], rep[:,die] = fit[pro], rep[:,pro]
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
        opi[:, die] = opi[:, pro]
    return fit, opi, rep, stg

def run_on_proc(q, pr):
    fit = np.ones(N)
    opi = np.identity(N)
    stg = nprand.rand(N)
    if MU_IND == 0:
        ind = np.ones(N) * ITER
    else:
        ind = nprand.random_integers(0, ITER, N)
    ast = np.zeros(STEPS)
    arp = np.zeros(STEPS)
    ain = np.zeros(STEPS)
    for t in xrange(STEPS):
        if t % DUMP == 0:
            print 'proc %d: step %d' % (pr, t)
        rep = pagerank(opi) * opi.sum() / N
        ast[t] = stg.sum() / N
        if MU_IND == 0:
            arp[t] = rep[ITER].sum() / N
        else:
            arp[t] = rep.sum() / (N * (ITER + 1))
        ain[t] = ind.sum() / N
        fit, opi = interact(fit, opi, rep, stg, ind)
        fit, opi, rep, stg = evolve(fit, opi, rep, stg, ind)
    q.put({'fit':fit, 'stg':stg, 'ind':ind, 'rep':rep, 
           'ast':ast, 'arp':arp, 'ain':ain})

def run():
    q = Queue()
    for i in xrange(PROC):
        proc = Process(target=run_on_proc, args=(q,i))
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
