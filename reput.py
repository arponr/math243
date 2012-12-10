from __future__ import division
import numpy as np
import numpy.random as nprand
import random, sys, os, cPickle
from math import *
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
B = 2
# number of interactions per round
MEETS = 500
# mutation probability for strategy
MU_STG = .0001
# mutation probability for pagerank-iterations
MU_IND = 0 #MU_IND = .0001
# population size
N = 100
# number of rounds
STEPS = 5000
# console width
WIDTH = 50
# how often to print progress
DUMP = STEPS/WIDTH
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
# subtracted from thresholds
STG_DELTA = 0
# multiply strategy by this
STG_MULT = 1.

def wrand(weight):
    a = random.random() * weight.sum()
    for i, w in enumerate(weight):
        if a > w:
            a -= w
        else:
            return i

def normalise(A):
    return A / np.maximum(A.sum(0), 1)

def pagerank(A):
    B = normalise(A)
    x = np.zeros((ITER+1, len(B)))
    x[0] = 1 / len(B)
    for i in xrange(ITER):
        x[i+1] = ALPHA * np.dot(B, x[i]) + (1 - ALPHA) / len(B)
    return x

def interact(fit, opi, rep, stg, ind):
    def interact_one(don, rec):
        new = 0
        if ((rep[ind[don]][rec] > stg[don] and random.random() > ERR) or
            (rep[ind[don]][rec] < stg[don] and random.random() < ERR)):
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
        stg[die] = random.random() * STG_MULT - STG_DELTA
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
    opi = np.zeros((N,N))
    stg = nprand.rand(N) * STG_MULT - STG_DELTA
    if MU_IND == 0:
        ind = np.ones(N) * ITER
    else:
        ind = nprand.random_integers(0, ITER, N)
    ast = np.zeros(STEPS)
    arp = np.zeros(STEPS)
    ain = np.zeros(STEPS)
    aft = np.zeros(STEPS)
    for t in xrange(STEPS):
        if t % DUMP == 0:
            q.put((pr, 'step', t))
        rep = pagerank(opi) * opi.sum() / N
        ast[t] = np.mean(stg)
        if MU_IND == 0:
            arp[t] = np.mean(rep[ITER])
        else:
            arp[t] = np.mean(rep)
        ain[t] = np.mean(ind)
        aft[t] = np.mean(fit)
        fit, opi = interact(fit, opi, rep, stg, ind)
        fit, opi, rep, stg = evolve(fit, opi, rep, stg, ind)
    q.put((pr, 'return', {'fit':fit, 'stg':stg, 'ind':ind, 'rep':rep, 
           'ast':ast, 'arp':arp, 'ain':ain, 'aft':aft}))

def run():
    q = Queue()
    if PROC > 1:
        for i in xrange(PROC):
            proc = Process(target=run_on_proc, args=(q,i))
            proc.start()
    else:
        run_on_proc(q, 0)
    arrs = {}
    steps = np.zeros(PROC)
    returns = 0
    wipe = ''
    faces = '])|([P\</O'
    f = 0
    while returns < PROC:
        pr, act, ret = q.get()
        if act == 'return':
            for (k, arr) in ret.iteritems():
                if not k in arrs:
                    arrs[k] = []
                arrs[k].append(arr)
            returns += 1
        elif act == 'step':
            steps[pr] = ret
            f = (f + 1) % len(faces)
            prog = '.' * int(floor(steps.sum() / (PROC*STEPS) * WIDTH)) + ' :' + faces[f]
            sys.stdout.write(wipe)
            sys.stdout.write(prog)
            wipe = "\b" * len(prog)
            sys.stdout.flush()
    return arrs

if __name__ == "__main__":
    fname = sys.argv[1]
    params = sys.argv[2:]
    g = globals()
    sets = {}
    for param in params:
        name, expr = param.split('=',1)
        if not name in g:
            print 'WARNING: no param', name
        sets[name] = eval(expr)
    g.update(sets)
    if not fname.endswith('.out'):
        fname = fname + '.out'
    result = run()
    with open(fname, 'w') as out:
        cPickle.dump(result, out)
