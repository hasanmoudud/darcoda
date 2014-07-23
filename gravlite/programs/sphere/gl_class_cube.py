#!/usr/bin/env ipython3

##
# @file
# parameters for MultiNest.
# cube = [0,1]^ndim
# Holds representations for overall density,
# [tracer density, anisotropy]_{for each population}
# Gives access to density, population profiles,
# and calculate physical values from [0,1]
# populations are counted from 0 = first component,
# 1 = first additional component

# (c) 2013 ETHZ Pascal S.P. Steger

import numpy as np
import pdb


def map_nr(pa, scale, width, gp):
    # get offset and n(r) profiles, calculate rho
    iscale = gp.iscale
    maxrhoslope = gp.maxrhoslope
    nrscale = gp.nrtol
    monotonic = gp.monotonic

    # first parameter gives half-light radius value of rho directly
    # use [0,1]**3 to increase probability of sampling close to 0
    # fix value with tracer densities,
    # sample a flat distribution over log(rho_half)
    pa[0] = 10**((pa[0]*2.*width)-width+np.log10(scale))

    # nr(r=0) is = rho slope for approaching r=0 asymptotically, given directly
    # should be smaller than -3 to exclude infinite enclosed mass
    if 1 <= iscale + 1:
        pa[1] = (pa[1]**1)*2.0
    else:
        pa[1] = (pa[1]**1)*2.999

    # offset for the integration of dn(r)/dlog(r) at smallest radius
    if 2 <= iscale + 1:
        pa[2] = (pa[2]**1)*2.0
    else:
        pa[2] = (pa[2]**1)*maxrhoslope

    rdef = gp.xepol
    for i in range(3, gp.nepol-1):
        # all -dlog(rho)/dlog(r) at data points and 2,4,8rmax can
        # lie in between 0 and gp.maxrhoslope
        if monotonic:
            # only increase n(r), use pa[i]>=0 directly
            pa[i] = pa[i-1]+pa[i]*nrscale*(np.log(rdef[i-2])-np.log(rdef[i-3]))
        else:
            # use pa => [-1, 1] for full interval
            pa[i] = pa[i-1]+(pa[i]-0.5)*2. * nrscale * (np.log(rdef[i-2])-np.log(rdef[i-3]))

        pa[i] = max(0., pa[i])
        if i <= iscale+1: # iscale: no. bins with xipol<Rscale[all]
            pa[i] = min(2.0, pa[i])
        else:
            pa[i] = min(maxrhoslope, pa[i])
    # rho slope for asymptotically reaching r = \infty is given directly
    # must lie below -3
    # to ensure we have a finite mass at all radii 0<r<=\infty
    pa[gp.nepol-1] = pa[gp.nepol-1] * maxrhoslope
    if monotonic:
        pa[gp.nepol-1] += pa[gp.nepol-2]
    # finite mass prior: to bound between 3 and gp.maxrhoslope, favoring 3:
    # pa[gp.nepol-1] = max(pa[gp.nepol-1], 3.)
    return pa
## \fn map_nr(pa, scale, width, gp)
# mapping nr and rho parameters from [0,1] to full parameter space
# setting all n(r<r_{iscale})<=2.0
# and possibly a monotonically increasing function
# first parameter is offset for rho_half
# second parameter is asymptotic n(r\to0) value
# @param pa cube [0,1]^ndim
# @param scale rho(r_half) [Munit/pc^3]
# @param width [dex] in log10 space
# @param gp global parameters


def map_nu(pa, gp):
    for i in range(gp.nupol):
        pa[i] = 10**(pa[i]*(gp.maxlog10nu-gp.minlog10nu)+gp.minlog10nu)
    return pa
## \fn map_nu(pa, gp)
# map tracer densities, directly
# @param pa cube [0,1]^n
# @param gp global parameters


def map_betastar(pa, gp):
    off = 0
    # beta* parameters : [0,1] ->  some range, e.g. [-1,1]
    # starting offset in range [-1,1]
    # cluster around 0, go symmetrically in both directions,
    pa[0] = 2.*(pa[0]-0.5)
    # out to maxbetaslope
    # here we allow |beta_star,0| > 1, so that any models with
    # beta(<r_i) = 1, beta(>r_i) < 1
    # are searched as well
    # pa[0] = np.sign(tmp)*tmp**2 # between -1 and 1 for first parameter
    off += 1
    for i in range(gp.nbeta-1):
        pa[off] = (2*(pa[off]-0.5))*gp.maxbetaslope
        # rising beta prior would remove -0.5
        # /i in the end suppresses higher order wiggling
        off += 1
    return pa
## \fn map_betastar(pa)
# mapping beta parameters from [0,1] to full parameter space
# @param pa parameter array


class Cube:
    def __init__ (self, gp):
        self.pops = gp.pops
        # for density and (nu, beta)_i
        self.cube = np.zeros(gp.ndim)
        return
    ## \fn __init__ (self, gp)
    # constructor, with modes depending on locpop
    # @param gp


    def convert_to_parameter_space(self, gp):
        # if we want any priors, here they have to enter:
        off = 0
        pc = self.cube
        # DM density rho, set in parametrization of n(r)
        tmp_nr = map_nr(pc[0:gp.nepol], gp.rhohalf, gp.rhospread, gp)
        for i in range(gp.nepol):
            pc[off+i] = tmp_nr[i]
        off += gp.nepol

        # rho*
        tmp_rhostar = map_nu(pc[off:off+gp.nupol], gp)
        for i in range(gp.nupol):
            pc[off+i] = tmp_rhostar[i]
        off += gp.nupol
        
        for pop in range(gp.pops): # nu1, nu2, ...
            tmp_nu = map_nu(pc[off:off+gp.nupol], gp)
            for i in range(gp.nupol):
                pc[off+i] = tmp_nu[i]
            off += gp.nupol
            tmp_betastar = map_betastar(pc[off:off+gp.nbeta], gp)
            for i in range(gp.nbeta):
                pc[off+i] = tmp_betastar[i]
            off += gp.nbeta
        return pc
    ## \fn convert_to_parameter_space(self, gp)
    # convert [0,1]^ndim to parameter space
    # such that values in cube are the parameters we need for rho, nu_i, beta_i
    # @param gp
    

    def __repr__(self):
        return "Cube: "+self.pops+" populations"
    ## \fn __repr__(self)
    # string representation for ipython

    
    def copy(self, cub):
        self.cube = cub
        return self
    ## \fn copy(self, cub)
    # copy constructor

## \class Cube
# Common base class for all parameter sets