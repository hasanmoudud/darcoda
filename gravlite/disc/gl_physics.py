#!/usr/bin/env python3

##
# @file
# calculations for velocity dispersion
# disc version

# (c) 2013 Pascal Steger, psteger@phys.ethz.ch

import pdb
import numpy as np
import scipy
from scipy.interpolate import splrep, splint
import gl_helper as gh


def nr(dlr, gp):
    # extend asymptotes to 0, and high radius
    r0 = gp.xepol
    r0 = np.hstack([r0[0]/1e4, r0[0]/2., r0, gp.rinfty*r0[-4]])
    logr0 = np.log(r0/gp.rstarhalf)
    dlr = np.hstack([dlr[0], dlr]) # dlr[-1]])
    dlr *= -1.
    
    # use linear spline interpolation in r
    spline_n = splrep(logr0, dlr, k=1)
    
    # evaluate spline at any points in between
    return spline_n #, splev(r0, spline_n)
## \fn nr(r0, dlogrhodlogr, gp)
# calculate n(r) at any given radius, as linear interpolation with two asymptotes
# @param dlogrhodlogr : asymptote at 0, n(r) for all bins, asymptote at infinity
# @param r0 bin centers in [pc]


def nr_medium(dlr, gp):
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
    logr0 = np.log(r0/gp.rstarhalf)
    dlr = np.hstack([dlr[0], dlr, dlr[-1]]) # 1+Nbin+2 entries
    dlr *= -1.
    
    # use linear spline interpolation in r
    spline_n = splrep(logr0, dlr, k=1)
    # evaluate spline at any points in between
    return spline_n #, splev(r0, spline_n)
## \fn nr_medium(binmin, binmax, dlogrhodlogr, gp)
# calculate n(r) at any given radius, as linear interpolation with two asymptotes
# @param dlogrhodlogr : asymptote at 0, n(r) for all bins at outsides of bin, asymptote at infinity
#                       1+Nbin+1 entries in [log Msun/pc^3/(log pc)]
# @param binmin minimum of bins, Nbin entries in [pc]
# @param binmax minimum of bins, Nbin entries in [pc]


def rho(r0, arr, gp):
    rhoathalf = arr[0]
    arr = arr[1:]

    spline_n = nr_medium(arr, gp) # extrapolate on gp.xepol, as this is where definition is on
    # spline_n_direct = nr(arr, gp) # fix on gp.xepol, as this is where definition is on

    rs =  np.log(r0/gp.rstarhalf) # have to integrate in d log(r)

    # check assumption r_min < rstarhalf < r_max
    if min(rs)>0. or max(rs)<0.:
        print('assumption r_min < rstarhalf < r_max violated')
        pdb.set_trace()
    logrright = rs[(rs>=0.)]
    logrleft  = rs[(rs<0.)]
    logrleft  = logrleft[::-1]
    logrhoright = []

    # integrate to left and right of halflight radius
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
## \fn rho(r0, arr, gp)
# calculate density, from interpolated n(r) = -log(rho(r))
# using interpolation to left and right of r=r_{*, 1/2}
# @param arr: rho(rstarhalf), asymptote_0, nr(gp.xipol), asymptote_infty
# @param r0: radii to calculate density for, in physical units (pc)
# @param gp global parameters


def beta(xipol, param, gp):
    betatmp = 0.
    for i in range(gp.nbeta):
        betatmp += param[i]*(xipol/max(gp.xipol))**i
    return betatmp
## \fn beta(xipol, param, gp)
# return sum of polynomials for tilt as fct of radius
# TODO: get tilt size from Silvia's paper
# @param xipol [pc]
# @param param n_beta parameters
# @param gp global parameters


def kappa(xipol, Kz):
    r0 = xipol
    kzpars = -np.hstack([Kz[0]/r0[0], (Kz[1:]-Kz[:-1])/(r0[1:]-r0[:-1])])
    return kzpars
## \fn kappa(xipol, Kz)
# calculate vertical force from Kz
# @param xipol height above midplane [pc]
# @param Kz acceleration in z direction


def nu_decrease(z, zpars, pars, gp):
    parsu = abs(pars)                        # Mirror prior
    
    if gp.monotonic:
        rnuz_z = np.zeros(len(zpars))
        rnuz_z[0] = parsu[0]
        for i in range(1,len(rnuz_z)):
            rnuz_z[i] = rnuz_z[i-1] + parsu[i]
        fun = rnuz_z[::-1]
    else:
        # Alternative here --> don't assume monotonic!
        fun = parsu
    
    # Normalise: 
    if not gp.quadratic:
        # Exact linear interpolation integral: 
        norm_nu = 0.
        for i in range(len(zpars)-1):
            zl = zpars[i]; zr = zpars[i+1]; zz = zr-zl
            b = fun[i]; a = fun[i+1]; norm_nu = norm_nu + (a-b)/2./zz*(zr**2.-zl**2.) + b*zr - a*zl
    else:
        # Exact quadratic interpolation:
        norm_nu = 0.
        for i in range(1,len(zpars)-1):
            z0 = zpars[i-1]; z1 = zpars[i]; z2 = zpars[i+1]
            f0 = fun[i-1];   f1 = fun[i];   f2 = fun[i+1]
            h = z2-z1
            a = f0; b = (f1-a)/h; c = (f2-2.*b*h-a)/2./h**2. 
            z1d = z1-z0; z2d = z1**2.-z0**2.; z3d = z1**3.-z0**3.
            
            if i == len(zpars)-2:
                # Last bin integrate from z0 --> z2: 
                z1d = z2-z0; z2d = z2**2.-z0**2.; z3d = z2**3.-z0**3.
            
            intquad = (a - b*z0 + c*z0*z1)*z1d + (b/2. - c/2.*(z0+z1))*z2d + c/3.*z3d
            norm_nu = norm_nu + intquad
            
            sel  = (z > z0 and z < z2)
            zcut = z[sel]
            tcut = testy[sel]

    fun /= norm_nu

    # Interpolate to input z:
    if not gp.quadratic:
        f = gh.ipol(zpars,fun,z)
    else:
        f = gh.ipol(zpars,fun,z)        # TODO: assure quadratic interpolation
    
    # Check for negative density:
    sel = (f>0)
    small = min(f[sel])
    for jj in range(len(f)):
        if (f[jj] < 0):
            f[jj] = small
    return f
## \fn nu_decrease(z, zpars, pars, gp)
# Fully non-parametric monotonic *decreasing* function [c.f. Kz function].
# Note, here we explicitly avoid rnuz_z(0) = 0 since this would correspond
# to a constraint rnu_z(zmax) = 0 which is only true if zmax = infty.
# @param z array of z values above plane
# @param zpars [pc]
# @param pars nu parametrization in bins
# @param gp global parameters


def kz(z_in, zpars, kzpars, blow, gp):
    # Mirror prior
    # kzparsu = abs(kzpars)
    
    # Assume here interpolation between dens "grid points", 
    # [linear or quadratic]. The grid points are stored 
    # in kzpars and give the *differential* increase in 
    # dens(z) towards small z [monotonic dens-prior]: 
    # denarr = np.zeros(gp.nipol)
    # denarr[0] = kzparsu[0]
    # for i in range(1,len(kzparsu)):
    #    denarr[i] = denarr[i-1] + kzparsu[i]
    # denarr = denarr[::-1]

    # override previous statements: use dens parameter directly, so denarr is really given by
    denarr = kzpars
    
    # Solve interpolated integral for Kz: 
    if not gp.quadratic:
        # Linear interpolation here: 
        kz_z = np.zeros(gp.nipol)
        for i in range(1,gp.nipol):
            zl = zpars[i-1]; zr = zpars[i]; zz = zr-zl
            b = denarr[i-1]; a = denarr[i]; kz_z[i] = kz_z[i-1]+(a-b)/2./zz*(zr**2.-zl**2.)+b*zr-a*zl
    else:
        # Quadratic interpolation here: 
        kz_z = np.zeros(gp.nipol)
        for i in range(1,gp.nipol-1):
            z0 = zpars[i-1];  z1 = zpars[i];  z2 = zpars[i+1]
            f0 = denarr[i-1]; f1 = denarr[i]; f2 = denarr[i+1]
            h = z2-z1; a = f0; b = (f1-a)/h; c = (f2-2.*b*h-a)/2./h**2.
            z1d = z1-z0; z2d = z1**2.-z0**2.; z3d = z1**3.-z0**3.
            intbit = (a-b*z0+c*z0*z1)*z1d+(b/2.-c/2.*(z0+z1))*z2d+c/3.*z3d
            kz_z[i] = kz_z[i-1] + intbit
            if i == n_elements(zpars)-2:
                # Deal with very last bin:
                z1d = z2-z1; z2d = z2**2.-z1**2.; z3d = z2**3.-z1**3.
                
                intbit = (a - b*z0 + c*z0*z1)*z1d + (b/2. - c/2.*(z0+z1))*z2d + c/3.*z3d
                kz_z[i+1] = kz_z[i] + intbit
    kz_out = kz_z # + blow # let blow alone, take overall Kz
    
    # Then interpolate back to the input array:
    #if not gp.quadratic:
    #    kz_out = gh.ipol(zpars,kz_z,z_in) #         # TODO: assure linear interpolation
    #else:
    #    kz_out = gh.ipol(zpars,kz_z,z_in) #         # TODO: quadratic!
        
    # Error checking. Sometimes when kz_z(0) << kz_z(1), 
    # the interpolant can go negative. This just means that 
    # we have resolved what should be kz_z(0) = 0. A simple
    # fix should suffice: 
    for jj in range(0,len(kz_out)):
        if (kz_out[jj] < 0):
            kz_out[jj] = 0.
        
    return kz_out
## \fn kz(z_in, zpars, kzpars, blow)
# General function to calculate the Kz force law:
# Non-parametric Kz function here. Use cumulative integral to
# ensure monotinicity in an efficient manner. Note here we
# use kz_z(0) = kzpars(0) * dz so that it can be zero, or
# otherwise just small in the case of large bins. This latter
# avoids the interpolated kz_out[0] going negative for coarse 
# binning.
# @param z_in input z heights [pc]
# @param zpars z where kzpars is defined on [pc]
# @param kzpars TODO
# @param blow lower bound, baryonic surface density
# @param gp


def sigmaz(zp, kzpars, nupars, norm, tpars, tparsR):
    # calculate density and Kz force:
    nu_z = nupars/np.max(nupars)          # normalized to 1
    # kz_z = kz(zp, zp, kzpars, blow, quadratic) # TODO: reenable
    kz_z = kzpars
    
    # add tilt correction [if required]:
    Rsun = tparsR[0]
    hr   = tparsR[1]
    hsig = tparsR[2]
    tc = sigma_rz(zp, zp, tpars)
    tc = tc * (1.0/Rsun - 1.0/hr - 1.0/hsig)
    # flag when the tilt becomes significant:
    if abs(np.sum(tc))/abs(np.sum(kz_z)) > 0.1:
        print('Tilt > 10%!', abs(np.sum(tc)), abs(np.sum(kz_z)))
    kz_z = kz_z-tc
    
    # do exact integral
    if not gp.quadratic:
        # linear interpolation here: 
        sigint = np.zeros(len(zp))
        for i in range(1,len(zp)):
            zl = zp[i-1];  zr = zp[i];  zz = zr-zl
            b = nu_z[i-1]; a = nu_z[i]; q = kz_z[i-1]; p = kz_z[i]
        
            intbit = (a-b)*(p-q)/(3.0*zz**2.) * (zr**3.-zl**3.) + \
                ((a-b)/(2.0*zz) * (q-(p-q)*zl/zz) + (p-q)/(2.0*zz)  * (b-(a-b)*zl/zz)) * (zr**2.-zl**2.)+\
                (b-(a-b)*zl/zz) * (q-(p-q)*zl/zz) * zz
      
            if i==0:
                sigint[0] = intbit
            else:
                sigint[i] = sigint[i-1] + intbit
    else:
        # quadratic interpolation
        sigint = np.zeros(len(zp))
        for i in range(1,len(zp)-1):
            z0 = zp[i-1];   z1 = zp[i];   z2 = zp[i+1]
            f0 = nu_z[i-1]; f1 = nu_z[i]; f2 = nu_z[i+1]
            fd0 = kz_z[i-1];fd1 = kz_z[i];fd2 = kz_z[i+1]
            h = z2-z1; a = f0; b = (f1-a)/h; c = (f2-2.*b*h-a)/2./h**2.
            ad = fd0; bd = (fd1-ad)/h; cd = (fd2-2.*bd*h-ad)/2./h**2.
            AA = a*bd+ad*b; BB = c*ad+cd*a; CC = b*cd+bd*c
            z1d = z1-z0; z2d = z1**2.-z0**2.; z3d = z1**3.-z0**3.; z4d = z1**4.-z0**4.; z5d = z1**5.-z0**5.
            intbit = z1d * (a*ad - z0*(AA-BB*z1) + z0**2.*(b*bd-CC*z1) + \
                        c*cd*z0**2.*z1**2.) + \
                        z2d * (0.5*(AA-BB*z1)-z0*(b*bd-CC*z1)-z0/2.*BB+z0**2./2.*CC - \
                        (z0*z1**2.+z0**2.*z1)*c*cd)+z3d*(1.0/3.0*(b*bd-CC*z1)+1.0/3.0*BB-2.0/3.0*z0*CC + \
                        1.0/3.0*c*cd*(z1**2.+z0**2.+4.0*z0*z1))+z4d*(1.0/4.0*CC-c*cd/2.0*(z1 + z0)) + \
                        z5d*c*cd/5.

            sigint[i] = sigint[i-1] + intbit
            if i == len(zp)-2:
                # Deal with very last bin: 
                z1d = z2-z1; z2d = z2**2.-z1**2.; z3d = z2**3.-z1**3.; z4d = z2**4.-z1**4.; z5d = z2**5.-z1**5.
                intbit = z1d * (a*ad - z0*(AA-BB*z1) + z0**2.*(b*bd-CC*z1) + \
                         c*cd*z0**2.*z1**2.) + \
                  z2d * (0.5*(AA-BB*z1)-z0*(b*bd-CC*z1) - z0/2.*BB + z0**2./2.*CC - \
                         (z0*z1**2. + z0**2.*z1)*c*cd) + \
                  z3d * (1.0/3.0*(b*bd-CC*z1)+1.0/3.0*BB - 2.0/3.0*z0*CC + \
                         1.0/3.0*c*cd*(z1**2. + z0**2. + 4.0*z0*z1)) + \
                  z4d * (1.0/4.0*CC - c*cd/2.0 * (z1 + z0)) + \
                  z5d * c*cd / 5.

                sigint[i+1] = sigint[i] + intbit
    sig_z_t2 = 1.0/nu_z * (sigint + norm)
    return  np.sqrt(sig_z_t2)
## \fn sigmaz(zp, kzpars, nupars, norm, tpars, tparsR)
# calculate z velocity dispersion
# @param zp vertical coordinate [pc]
# @param kzpars kappa to be integrated to give force
# @param nupars parameters for tracer density falloff
# @param norm value C, corresponds to integration from 0 to rmin
# @param tpars tilt parameters
# @param tparsR tilt parameters: Rsun, hr, hsig


def sigma_rz(z, zpars, tpars):
    # Mirror prior
    tparsu = abs(tpars)
    
    # dz = zpars[2]-zpars[1]
    # sig_Rz = np.zeros(gp.nipol)
    # sig_Rz[0] = tparsu[0] * dz / 2.
    # for i in range(1,gp.nipol):
    #   sig_Rz[i] = sig_Rz[i-1] + tparsu[i] * dz
    # f = gp.ipol(zpars,sig_Rz,z)
    
    # Alternative here --> don't assume monotonic!
    f = gh.ipol(zpars, tparsu, z)
    return f
## \fn sigma_rz(z, zpars, tpars)
# General function to describe the tilt profile
# @param z [pc]
# @param zpars [pc] z, on which sigma is defined
# @param tpars tilt parameters: Rsun, hr, hsig