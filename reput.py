from __future__ import division
import numpy as np
import numpy.random as nprand
import scipy.weave as weave
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
MEETS = 100
# mutation probability for strategy
MU_STG = .0001
# mutation probability for pagerank-iterations
MU_IND = 0 #MU_IND = .0001
# population size
N = 100
# number of rounds
STEPS = 20000
# console width
WIDTH = 80
# how often to print progress
PROG = STEPS/WIDTH
# how often to snapshot all data
DUMP = STEPS
# number of threads
PROC = 4
#number of simulations per thread
SIM = 4
# reset everyone's opinions of offspring
DIE_RESET = False
# error rate in actions
ERR = 0.
# chance for an action to be heard about
GOS = 1.
# true: interact round-robin; false: interact randomly
ROBIN = False
# true: remember the past (with discounting); false: don't
MEMORY = 0
# chance of unconditional cooperators
PERC = .05
# chance of unconditional defectors
PERD = .05

def wrand(weight):
    a = random.random() * weight.sum()
    for i, w in enumerate(weight):
        if a > w:
            a -= w
        else:
            return i

def normalise(A):
    B = A / np.maximum(A.sum(0), 1)
    return B + (1 - B.sum(0)) / len(B)

def pagerank(A):
    B = normalise(A)
    x = np.zeros((ITER+1, len(B)))
    x[0] = 1 / len(B)
    for i in xrange(ITER):
        x[i+1] = ALPHA * np.dot(B, x[i]) + (1 - ALPHA) / len(B)
    return x

def strategy_from(rand):
    return rand /(1 - PERC - PERD) - PERC/(1 - PERC - PERD)

robin_dons = np.array(range(N)*(N-1))
robin_recs = np.array(range(N-1)*N)
def interact(fit, opi, rep, stg, ind):
    m = MEETS
    if ROBIN:
        m = N * (N-1)
        dons = robin_dons
        recs = robin_recs
    else:
        dons = nprand.random_integers(0, N-1, m)
        recs = nprand.random_integers(0, N-2, m)
    if ERR > 0:
        rands = nprand.rand(m)
    else:
        rands = np.ones(m)
    if GOS < 1:
        sands = nprand.rand(m)
    else:
        sands = np.zeros(m)
    coops = np.zeros(1)
    code = r'''
#line 84 "reput.c"
int don, rec;
double newval;
for (int t = 0; t < m; t++) {
    don = dons(t);
    rec = recs(t);
    if (rec >= don) {
        rec += 1;
    }
    newval = 0;
    if ((rep((int) ind(don),rec) > stg(don) && rands(t) > ERR) || rands(t) < ERR) {
        newval = (sands(t) < GOS) ? 1 : opi(don, rec);
        fit(don) -= C * SEL;
        fit(rec) += B * SEL;
        coops(0) += 1;
    }
    if (MEMORY) {
        opi(don, rec) = (opi(don, rec) + newval/2) / 2;
    }
    else {
        opi(don, rec) = newval;
    }
}
'''
    weave.inline(code, ['m', 'dons', 'recs', 'MEMORY', 'ERR', 'rands', 'sands',
                        'stg', 'fit', 'opi', 'B', 'C', 'SEL', 'GOS', 'rep', 'ind', 'coops'],
                 type_converters=weave.converters.blitz)
    return fit, opi, coops[0]
    
def evolve(fit, opi, rep, stg, ind):
    pro = wrand(fit)
    die = random.randrange(N)
    fit[die], rep[:,die] = fit[pro], rep[:,pro]
    if random.random() < MU_STG:
        stg[die] = strategy_from(random.random())
    else:
        stg[die] = stg[pro]
    if random.random() < MU_IND:
        ind[die] = random.randrange(ITER+1)
    else:
        ind[die] = ind[pro]
    if DIE_RESET:
        opi[die] = 0
        opi[:,die] = 0
    else:
        opi[die] = opi[pro]
        opi[:, die] = opi[:, pro]
        opi[die, die] = 0
    return fit, opi, rep, stg

def run_on_proc(q, pr):
    for i in xrange(SIM):
        fit = np.ones(N)
        opi = np.zeros((N, N))
        stg = strategy_from(nprand.rand(N))
        if MU_IND == 0:
            ind = np.ones(N, int) * ITER
        else:
            ind = nprand.random_integers(0, ITER, N)
        ast = np.zeros(STEPS)
        arp = np.zeros(STEPS)
        ain = np.zeros(STEPS)
        aft = np.zeros(STEPS)
        pst = np.zeros((STEPS/DUMP,N))
        prp = np.zeros((STEPS/DUMP,N))
        pin = np.zeros((STEPS/DUMP,N))
        pft = np.zeros((STEPS/DUMP,N))
        cps = np.zeros(STEPS)
        for t in xrange(STEPS):
            if t % PROG == 0:
                q.put((pr, 'step', t + i*STEPS))                
            rep = np.minimum(1, pagerank(opi) * opi.sum() / (N-1))
            ast[t] = np.mean(stg)
            if MU_IND == 0:
                arp[t] = np.mean(rep[ITER])
            else:
                arp[t] = np.mean(rep)
                # prp not defined in this case yet
            ain[t] = np.mean(ind)
            fit, opi, coops = interact(fit, opi, rep, stg, ind)
            cps[t] = coops
            fit, opi, rep, stg = evolve(fit, opi, rep, stg, ind)
            aft[t] = np.mean(fit)
            if t % DUMP == 0:
                pst[t/DUMP] = stg.copy()
                prp[t/DUMP] = rep[ITER].copy()
                pin[t/DUMP] = ind.copy()
                pft[t/DUMP] = fit.copy()
            fit = np.ones(N)
        q.put((pr, 'return', {'fit':fit, 'stg':stg, 'ind':ind,
                              'rep':rep, 'ast':ast, 'arp':arp,
                              'ain':ain, 'aft':aft, 'cps':cps}))
                              #'pst':pst,
                              #'prp':prp, 'pin':pin, 'pft':pft}
                              #'cps':cps})) 
        
def avg_trials(arrs):
    avgs = {}
    for k, arr in arrs.iteritems():
        avgs['avg_'+k] = np.mean(np.array(arr), 0)
    return avgs

def run():
    q = Queue()
    if PROC > 1:
        for i in xrange(PROC):
            proc = Process(target=run_on_proc, args=(q, i))
            proc.start()
    else:
        run_on_proc(q, 0)    
    arrs = {}
    steps = np.zeros(PROC*SIM)
    returns = 0
    wipe = ''
    faces = '])|([P\</O'
    f = 0
    while returns < PROC*SIM:
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
            prog = '.' * int(floor(steps.sum() / (PROC*SIM*STEPS) * (WIDTH-3))) + ' :' + faces[f]
            sys.stdout.write(wipe)
            sys.stdout.write(prog)
            wipe = "\b" * len(prog)
            sys.stdout.flush()
    #arrs.update(avg_trials(arrs))
    arrs['params'] = dict((k,v) for k, v in globals().iteritems() 
                          if k.upper() == k)
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
    print N, MEETS, ITER, SEL
    result = run()
    with open(fname, 'w') as out:
        cPickle.dump(result, out)
    print
