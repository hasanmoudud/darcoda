#!/usr/bin/env ipython3

##
# @file
# all functions working on spherical coordinates

# (c) 2013 Pascal Steger, psteger@phys.ethz.ch

import pdb
import numpy as np
import gl_chi as gc
import gl_helper as gh

from scipy.interpolate import splrep, splint
from gl_analytic import *
import gl_int as gi

def rhodm_hernquist(r, rho0, r_DM, alpha_DM, beta_DM, gamma_DM):
    return rho0*(r/r_DM)**(-gamma_DM)*\
      (1+(r/r_DM)**alpha_DM)**((gamma_DM-beta_DM)/alpha_DM)
## \fn rhodm_hernquist(r,rho0,r_DM,alpha_DM,beta_DM,gamma_DM)
# return hernquist DM density from generalized Hernquist profile
# @param r radius in [pc]
# @param rho0 central 3D density in [Munit/pc^3]
# @param r_DM scale radius of dark matter, [pc]
# @param alpha_DM [1]
# @param beta_DM [1]
# @param gamma_DM [1] central density slope

      
def nr(dlr, pop, gp):
    # extend asymptotes to 0, and high radius
    r0 = gp.xepol
    r0 = np.hstack([r0[0]/1e4, r0[0]/2., r0, gp.rinfty*r0[-4]])
    logr0 = np.log(r0/gp.Rscale[pop])
    # up: common radii r0, but different scale radius for each pop
    dlr = np.hstack([dlr[0], dlr]) # dlr[-1]])
    dlr *= -1.
    
    # use linear spline interpolation in r
    spline_n = splrep(logr0, dlr, k=1)
    
    # evaluate spline at any points in between
    return spline_n
## \fn nr(dlogrhodlogr, pop, gp)
# calculate n(r) at any given radius, as linear interpolation with two asymptotes
# @param dlogrhodlogr : asymptote at 0, n(r) for all bins, asymptote at infinity
# @param pop int for population (both, 1, 2, ...)
# @param gp global parameters


def nr_medium(dlr, pop, gp):
    binmin = np.hstack([gp.dat.binmin[0]/1e4, \
                        gp.dat.binmin[0]/2., \
                        gp.dat.binmin, \
                        gp.dat.binmax[-1], \
                        3.*gp.xepol[-4], \
                        # gp.xepol[-4] is last data bin radius
                        5.*gp.xepol[-4], \
                        11.*gp.xepol[-4]])
                        
    binmax = np.hstack([gp.dat.binmin[0]/2., \
                        gp.dat.binmin[0], \
                        gp.dat.binmax, \
                        3*gp.xepol[-4], \
                        5.*gp.xepol[-4], \
                        11.*gp.xepol[-4], \
                        (2*gp.rinfty-11.)*gp.xepol[-4]])

    # gpl.plot(gp.xepol, 1*np.ones(len(gp.xepol)), 'b.')
    # gpl.plot(gp.rinfty*gp.xepol[-4], 1, 'b.')
    # gpl.plot(binmin, np.zeros(len(binmin)), '.')
    # gpl.plot(binmax, 2*np.ones(len(binmax)), '.')
    # gpl.ylim([-4, 4])
    # gpl.xscale('log')

    
    # extend asymptotes to 0, and high radius
    r0 = np.hstack([binmin, binmax[-1]])
    # 1+(Nbin+1)+1 entries
    logr0 = np.log(r0/gp.Rscale[pop])
    dlr = np.hstack([dlr[0], dlr, dlr[-1]]) # 1+Nbin+2 entries
    dlr *= -1.
    
    # use linear spline interpolation in r
    spline_n = splrep(logr0, dlr, k=1)
    # evaluate spline at any points in between
    return spline_n #, splev(r0, spline_n)
## \fn nr_medium(dlogrhodlogr, pop, gp)
# calculate n(r) at any given radius, as linear interpolation with two asymptotes
# @param dlogrhodlogr : asymptote at 0, n(r) for all bins at outsides of bin, asymptote at infinity
#                       1+Nbin+1 entries in [log Munit/pc^3/(log pc)]
# @param pop int for population (0 both, 1, 2..)
# @param gp global parameters


def rho(r0, arr, pop, gp):
    rhoathalf = arr[0]
    arr = arr[1:]

    # spline_n = nr_medium(arr, pop, gp) # extrapolate
    spline_n = nr(arr, pop, gp) # fix on gp.xepol, where it's defined

    rs =  np.log(r0/gp.Rscale[pop]) # have to integrate in d log(r)

    logrright = rs[(rs>=0.)]
    logrleft  = rs[(rs<0.)]
    logrleft  = logrleft[::-1]
    logrhoright = []

    for i in np.arange(0, len(logrright)):
        logrhoright.append(np.log(rhoathalf) + \
                           splint(0., logrright[i], spline_n))
                           # integration along dlog(r) instead of dr

    logrholeft = []
    for i in np.arange(0, len(logrleft)):
        logrholeft.append(np.log(rhoathalf) + \
                          splint(0., logrleft[i], spline_n))

    tmp = np.exp(np.hstack([logrholeft[::-1], logrhoright])) # still defined on log(r)
    gh.checkpositive(tmp, 'rho()')
    return tmp
## \fn rho(r0, arr, pop, gp)
# calculate density, from interpolated n(r) = -log(rho(r))
# using interpolation to left and right of r=r_{*, 1/2}
# @param arr rho(rstarhalf), asymptote_0, nr(xipol), asymptote_infty
# @param r0 radii to calculate density for, in physical units (pc)
# @param pop int for population, 0 all or DM, 1, 2, ...
# @param gp global parameters


def beta_star_to_beta(betastar):
    # beta^* = \frac{sig_r^2-sig_t^2}{sig_r^2+sig_t^2}
    # betastar is in [-1,1]
    # and symmetric
    return 2.*betastar/(1.+betastar)
## \fn beta_star_to_beta(betastar)
# map beta* to beta
# @param betastar float array


def map_beta_star_poly(r0, arr, gp):
    r0 = np.array([r0]).flatten()
    betatmp = np.zeros(len(r0))
    for i in range(gp.nbeta):
        betatmp += arr[i] * (r0/max(gp.xipol))**i
    # clipping beta* to the range [-1,1]
    # thus not allowing any unphysical beta,
    # but still allowing parameters to go the the max. value
    
    for i in range(len(r0)):
        if betatmp[i] > 1.:
            betatmp[i] = 1.
        if betatmp[i] <= -1.:
            betatmp[i] = -0.99999999999 # excluding -inf values in beta
    return betatmp
## \fn map_beta_star_poly(r0, arr, gp)
# map [0,1] to [-1,1] with a polynomial
# @param r0 radii [pc]
# @param arr normalized ai, s.t. abs(sum(ai)) = 1
# @param gp global parameters


def beta(r0, arr, gp):
    betastar = map_beta_star_poly(r0, arr, gp)
    betatmp  = beta_star_to_beta(betastar)
    return betatmp, betastar
## \fn beta(r0, arr, gp)
# return beta and beta* from beta parameter array
# @param r0 radii [pc]
# @param arr float array, see gl_class_cube
# @param gp global parameters


def calculate_rho(r, M):
    r0 = np.hstack([0,r])                         # [lunit]
    M0 = np.hstack([0,M])

    deltaM   = M0[1:]-M0[:-1]                     # [Munit]
    gh.checkpositive(deltaM,  'unphysical negative mass increment encountered')

    deltavol = 4./3.*np.pi*(r0[1:]**3-r0[:-1]**3) # [lunit^3]
    rho     = deltaM / deltavol                  # [Munit/lunit^3]
    gh.checkpositive(rho, 'rho in calculate_rho')
    return rho                                   # [Munit/lunit^3]
## \fn calculate_rho(r, M)
# take enclosed mass, radii, and compute 3D density in shells
# @param r radius in [pc]
# @param M enclosed mass profile, [Munit]


def calculate_surfdens(r, M):
    r0 = np.hstack([0,r])                         # [lunit]
    M0 = np.hstack([0,M])                         # [Munit]

    deltaM = M0[1:]-M0[:-1]                       # [Munit]
    gh.checkpositive(deltaM, 'unphysical negative mass increment encountered')
    
    deltavol = np.pi*(r0[1:]**2 - r0[:-1]**2)        # [lunit^2]
    Rho = deltaM/deltavol                           # [Munit/lunit^2]
    gh.checkpositive(Rho, 'Rho in calculate_surfdens')
    return Rho                                      # [Munit/lunit^2]
## \fn calculate_surfdens(r, M)
# take mass(<r) in bins, calc mass in annuli, get surface density
# @param r radius in [pc]
# @param M 3D mass profile


def sig_kap_zet(r0, rhopar, rhostarpar, nupar, betapar, pop, gp):
    from gl_project import rho_param_INT_Rho
    surfden = rho_param_INT_Rho(r0, rhopar, pop, gp)
    siglos2surf, kaplos4surf, zetaa, zetab = gi.ant_sigkaplos2surf(r0, rhopar, rhostarpar, nupar, betapar, pop, gp)

    siglos2 = siglos2surf/surfden   # [(km/s)^2]
    siglos  = np.sqrt(siglos2)           # [km/s]

    if gp.usekappa:
        kaplos4     = kaplos4surf/surfden
        # takes [Munit/pc^2 (km/s)^2], gives back [(km/s)^2]
        
        kaplos = kaplos4/(siglos2**2)
        # - 3.0 # subtract 3.0 for Gaussian distribution in Fisher version.
    else:
        kaplos = 3.*np.ones(len(siglos))
    # TODO check if zetaa, zetab need factor 1/surfden

    return siglos, kaplos, zetaa, zetab  # [km/s], [1]
## \fn sig_kap_zet(r0, rhopar, rhostarpar, nupar, betapar, pop, gp)
# General function to calculate sig_los
# with analytic integral over fitting polynomial'
# @param r0 radius [pc]
# @param rhopar [1]
# @param rhostarpar [1]
# @param nupar 1D array 3D tracer density parameters [1]
# @param betapar 1D array 3D velocity anisotropy parameters [1]
# @param pop int population to take halflight radius from
# @param gp global parameters
