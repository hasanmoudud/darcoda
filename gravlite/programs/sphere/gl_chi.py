#!/usr/bin/env ipython3

##
# @file
# all functions called directly from gravlite

# (c) ETHZ 2013 Pascal Steger, psteger@phys.ethz.ch

from types import *
import pdb
import numpy as np
import numpy.random as npr

import gl_analytic as ga
# import gl_class_profiles as glp

def chi2red(model, data, sig, dof):
    # if Degrees Of Freedom = 1, return non-reduced chi2
    model = np.array(model)
    data  = np.array(data)
    sig   = np.array(sig)
    return np.sum(((model-data)**2./sig**2.)/dof)
## \fn chi2red(model, data, sig, dof)
# determine 'reduced chi2'
# @param model profile
# @param data profile
# @param sig spread
# @param dof Degrees Of Freedom


def calc_chi2(profs, gp):
    chi2 = 0.

    Sigdat = gp.dat.Sig[0]              # [Munit/pc^2] from rho*
    Sigerr = gp.dat.Sigerr[0]           # [Munit/pc^2]
    Sigmodel = profs.get_prof('Sig', 0)
    chi2_rhostar = chi2red(Sigmodel, Sigdat, Sigerr, gp.nipol) # [1]
    chi2 += chi2_rhostar
    print('chi2_rhostar     = ', chi2_rhostar)

    # now run through the stellar tracers
    for pop in np.arange(1, gp.pops+1): # [1, 2, ... , pops]
        Sigdat   = gp.dat.Sig[pop]      # [Munit/pc^2]
        Sigerr   = gp.dat.Sigerr[pop]   # [Munit/pc^2]
        Sigmodel = profs.get_prof('Sig', pop)
        chi2_Sig  = chi2red(Sigmodel, Sigdat, Sigerr, gp.nipol) # [1]
        chi2 += chi2_Sig                 # [1]
        
        sigdat  = gp.dat.sig[pop]    # [km/s]
        sigerr  = gp.dat.sigerr[pop]    # [km/s]
        chi2_sig = chi2red(profs.get_prof('sig', pop), sigdat, sigerr, gp.nipol) # [1]
        chi2 += chi2_sig                # [1]
        print('chi2_{Sig, sig} = ', chi2_Sig, ' ', chi2_sig)
        if gp.usekappa:
            kapdat  = gp.dat.kap[pop] # [1]
            kaperr  = gp.dat.kaperr[pop] # [1]
            chi2_kap = chi2red(profs.get_kap(pop), kapdat, kaperr, gp.nipol) # [1]
            chi2 += chi2_kap            # [1]
        # TODO: check
        # if gp.usezeta:
        #     zetaadat = gp.dat.zetaadat[pop]
        #     zetabdat = gp.dat.zetabdat[pop]
        #     zetaaerr = gp.dat.zetaaerr[pop]
        #     zetaberr = gp.dat.zetaberr[pop]
        #     chi2_zetaa = chi2red(profs.get_prof('zetaa', pop), zetaadat, zetaaerr, gp.nipol)
        #     chi2_zetab = chi2red(profs.get_prof('zetab', pop), zetabdat, zetaberr, gp.nipol)
        #     chi2 += (chi2_zetaa + chi2_zetab)
    return chi2
## \fn calc_chi2(profs, gp)
# Calculate chi^2
# @param profs profiles for rho, M, rho*, nu_i, beta_i, sig_i, kap_i
# @param gp global parameters
