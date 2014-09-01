#!/usr/bin/env python3

## @file
# split populations in observed dwarf galaxies
# based on metallicity, Mg index, v_LOS, position

# (c) 2013 Pascal S.P. Steger

import numpy as np
import sys, pdb
import gr_params as gpr
import gl_helper as gh
from gl_centering import com_shrinkcircle_v_2D
import pymultinest


def p_plummer(R, rs):
    return np.log(2.*R/rs**2/(1.+R**2/rs**2)**2)
## \fn p_plummer(R, rh)
# eq. 8 Walker 2011, likelihood that a tracer star is member of Plummer sphere
# @param R projected radius from center, [arcmin]
# @param rs scale radius, [arcmin]


def p_gauss(X, Xmean, sigmaX, errorX):
    prefactor = 1./np.sqrt(2.*np.pi*(sigmaX**2+errorX**2))
    exponent = -0.5*(X-Xmean)**2/(sigmaX**2+errorX**2)
    return np.log(prefactor*np.exp(exponent))
## \fn p_gauss(X, Xmean, sigmaX, errorX)
# eq. 9, 11 Walker 2011, likelihood based on generic Gauss function
# @param X variable, property of stellar tracer
# @param Xmean mean of all stars in that population
# @param sigmaX spread of Gaussian
# @param errorX observation error


def p_MW(Xi, PMi, error):
    nom = 0.
    denom = 0.
    for i in range(len(Xi)):
        nom += (1.-PMi[i])/np.sqrt(2.*np.pi*error**2)*np.exp(-0.5*(Xi[i]-X)**2/error[i]**2)
        denom += (1.-PM[i])
    return np.log(nom/denom)
## \fn p_MW(Xi, PMi, error)
# eq. 12 generic Walker 2011, likelihood that star is MW foreground
# @param Xi variable, property of stellar tracer
# @param PMi probability of membership
# @param error observation error


def pR(Rk, pop):
    return p_gauss(Rk, Rmean[pop], sigmaR[pop], errorR[pop])
## \fn pR(Rk, pop)
# eq. 8 Walker 2011, probability distribution of radii
# @param Rk radius of stellar tracer k, [arcmin]
# @param pop int for population (0: MW, 1: 1, ...)


def pV(Vk, pop):
    return p_gauss(Vk, Vmean[pop], sigmaV[pop], errorV[pop])


def pW(Wk, pop):
    return p_gauss(Wk, Wmean[pop], sigmaW[pop], errorW[pop])


def pjoint(Rk, Vk, Wk, PMk, pop):
    if pop == 0:
        pR = p_MW(Rk, PMk, Rerror)
        pV = p_MW(Vk, PMk, Verror)
        pW = p_MW(Wk, PMk, Werror)
        return pR*pV*pW
    else:
        return pR(Rk, pop)*pV(Vk, pop)*pW(Wk, pop)
## \fn pjoint(Rk, Vk, Wk, PMk, pop)
# eq. 13 Walker 2011, joint probability distributions
# @param Rk projected radius, [arcmin]
# @param Vk LOS velocity [km/s]
# @param Wk reduced magnesium index [Ang]
# @param PMk probability of membership


def Vmean(ds, als, Vd, dd, ad, mud, mua, D):
    from numpy import sin, cos
    Vm = cos(ds)*sin(als)*(Vd*cos(dd)*sin(ad)+D*mua*cos(dd)*cos(ad)-D*mud*sin(dd)*sin(ad))\
         +cos(ds)*cos(als)*(Vd*cos(dd)*cos(ad)\
                           -D*mud*sin(dd)*cos(ad)\
                           -D*mua*cos(dd)*sin(ad))\
         +sin(ds)*(Vd*sin(dd)+D*mud*cos(dd))
    return Vm
## \fn Vmean(ds, als, Vd, dd, ad, mud, mua, D)
# eq. 10 Walker 2011, dwarf spheroidal systemic HRF, [km/s]
# @param ds
# @param als
# @param Vd
# @param dd
# @param ad
# @param mud
# @param mua
# @param D


def show(filepath):
    subprocess.call(('xdg-open', filepath))
    return
## \fn show(filepath) open the output (pdf) file for the user @param
# filepath filename with full path


def myprior(cube, ndim, nparams):
    # convert to physical space
    cube[0] = cube[0] # fmem
    cube[1] = cube[1] # fsub
    cube[2] = 10**(4.5*cube[2]) # r_half [pc]

    cube[3] = cube[3]*2000.-1000. # proper motion in x [km/s]
    cube[4] = cube[4]*2000.-1000. # proper motion in y [km/s]
    off = 5 # offset from common parameters
    for pop in range(gp.pops+1): # no. of pops goes in here, first MW, then 1,2,..
        cube[off] = cube[off] # rhalf_i / r_half
        off += 1
        cube[off] = cube[off]*6.-3. # Wmean
        off += 1
        cube[off] = 10.**(cube[off]*6.-5.)  # sigmaW^2 [Angstrom^2]
        off += 1
        cube[off] = 10.**(cube[off]*10.-5.) # sigmaV^2 [(km/s)^2]
        off += 1
    return
## \fn myprior(cube, ndim, nparams) priors
# @param cube [0,1]^ndim cube, array of dimension ndim
# @param ndim number of dimensions, 2*npop*nipol + nipol 
# @param nparams = ndim + additional parameters
# stored with actual parameters


def myloglike(cube, ndim, nparams):
    ev = 0.
    fmem = cube[0]
    fsub = cube[1]
    f1 = fmem*fsub
    f2 = fmem*(1-fsub)
    ftot = [1-f1-f2, f1, f2]
    # TODO: calculate log likelihood of assigning stars to each population
    r_half = cube[2]
    vx0 = cube[3]
    vy0 = cube[4]
    off = 5
    for pop in range(gp.pops+1):
        rhalf_i = cube[off]*r_half
        off += 1
        Wmean = cube[off]
        off += 1
        sigW2 = cube[off]
        off += 1
        sigV2 = cube[off]
        off += 1
        
    logev = 0.0
    for k in range(Nsample):
        term = 0.0
        for pop in range(gp.pops+1):
            term += ftot[k] * w(Rk)*p(R[k], V[k], W[k], PM[k], pop)
        logev += np.log(term)
    return logev
## \fn myloglike(cube, ndim, nparams) calculate probability function
# @param cube ndim cube of physical parameter space (nr)
# @param ndim number of dimensions, 2*npop*nipol + nipol
# @param nparams = ndim + additional parameters
# stored with actual parameters


def prepare_data(gp):
    gpr.fil = gpr.dir+"/table_merged.bin"
    delim = [0,22,3,3,6,4,3,5,6,6,7,5,6,5,6,5,6]
    ID = np.genfromtxt(gpr.fil, skiprows=29, unpack=True,\
                       usecols=(0,1),delimiter=delim)
                       
    RAh,RAm,RAs,DEd,DEm,DEs,Vmag,VI,\
      VHel,e_VHel,SigFe,e_SigFe,\
      SigMg,e_SigMg,PM = np.genfromtxt(gpr.fil, skiprows=29, unpack=True, \
                                       usecols=tuple(range(2,17)), delimiter=delim, filling_values=-1)
    # use all stellar tracer particles from now on, independent on their probability of membership
    Mg0 = SigMg
    sig = abs(RAh[0])/RAh[0]
    print('RAh: signum = ',sig)
    RAh = RAh/sig
    xs = 15*(RAh*3600+RAm*60+RAs)*sig       # [arcsec/15]
    
    sig = abs(DEd[0])/DEd[0]
    print('DEd: signum = ',sig)
    DEd = DEd/sig
    ys = (DEd*3600+DEm*60+DEs)*sig          # [arcsec]

    arcsec = 2.*np.pi/(360.*60.*60) # [pc]

    kpc = 1000 # [pc]
    DL = {0: lambda x: x * (138),#+/- 8 for Fornax
          1: lambda x: x * (101),#+/- 5 for Carina
          2: lambda x: x * (79),  #+/- 4 for Sculptor
          3: lambda x: x * (86) #+/- 4 for Sextans
      }[gp.case](kpc)

    xs *= (arcsec*DL) # [pc]
    ys *= (arcsec*DL) # [pc]

    PM0 = np.copy(PM); x0 = np.copy(xs); y0 = np.copy(ys) # [pc]
    vz0 = np.copy(VHel) # [km/s]
## \fn prepare_data(gp)
# prepare everything for multinest.MPI run
# @param gp global parameters


def run(gp):
    n_dims = 12

    pymultinest.run(myloglike,   myprior,
                    n_dims,      n_params = n_dims+1, # None beforehands
                    n_clustering_params = n_dims, # separate modes on
                                                  # the rho parameters
                                                  # only (gp.nrho in
                                                  # this case)
                    wrapped_params = [ gp.pops, gp.nipol, gp.nrho], # do
                                                                     #not
                                                                     #wrap-around
                                                                     #parameters
                    importance_nested_sampling = True, # INS enabled
                    multimodal = False,            # separate modes
                    const_efficiency_mode = True, # use const sampling efficiency
                    n_live_points = gp.nlive,
                    evidence_tolerance = 0.0, # set to 0 to keep
                                              #algorithm working
                                              #indefinitely
                    sampling_efficiency = 0.05, # very low eff. in
                                                #case of const efficiency mode,
                                                #README
                    n_iter_before_update = 1, # output after this many iterations
                    null_log_evidence = 1., # separate modes if
                                            #logevidence > this param.
                    max_modes = gp.nlive,   # preallocation of modes:
                                            #max. = number of live
                                            #points
                    mode_tolerance = -1.e60,   # mode tolerance in the
                                               #case where no special
                                               #value exists: highly
                                               #negative
                    outputfiles_basename = gp.files.outdir,
                    seed = -1,
                    verbose = True,
                    resume = False,
                    context = 0,
                    write_output = True,
                    log_zero = 0,      # points with log likelihood
                                          #< log_zero will be
                                          #neglected
                    max_iter = 0,         # set to 0 for never
                                          #reaching max_iter (no
                                          #stopping criterium based on
                                          #number of iterations)
                    init_MPI = True,     # use MPI
                    dump_callback = None)


if __name__=='__main__':
    import gl_params
    gp = gl_params.Params()
    prepare_data(gp)
    run(gp)
