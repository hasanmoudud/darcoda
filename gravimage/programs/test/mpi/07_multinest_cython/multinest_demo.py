#!/usr/bin/env python3

import math, os
import multinest

if not os.path.exists("chains"): os.mkdir("chains")

# our probability functions
# Taken from the eggbox problem.
def myprior(cube, ndim, nparams):
    for i in range(ndim):
        cube[i] = cube[i] * 10 * math.pi

def myloglike(cube, ndim, nparams):
    chi = 1.
    for i in range(ndim):
        chi *= math.cos(cube[i] / 2.)
    return math.pow(2. + chi, 5)

# number of dimensions our problem has
parameters = ["x", "y"]
n_dims = len(parameters)

print('reached state before run')
# run MultiNest
multinest.run(myloglike,\
              myprior,\
              n_dims,\
              nest_resume = True, \
              nest_fb = True,\
              initMPI = False)

print('run successfully finished')