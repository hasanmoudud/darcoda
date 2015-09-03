#!/usr/bin/env ipython3

##
# @file
# all functions called directly from gravimage
# disc version, done

# (c) ETHZ 2013 Pascal Steger, psteger@phys.ethz.ch

#from types import *
import pdb
import numpy as np
import gl_helper as gh

def chi2func(model, data, sig):
    # if Degrees Of Freedom = 1, return non-reduced chi2
    model = np.array(model)
    data  = np.array(data)
    sig   = np.array(sig)
    chired = np.sum((model-data)**2./sig**2.)
    return chired
## \fn chi2func(model, data, sig)
# determine 'reduced chi2'
# @param model
# @param data
# @param sig spread


def calc_chi2(profs, gp):

    if gp.map_priors:
        return 1.0

    #Tracer population comparison
    for pop in range(0, gp.ntracer_pops):

        #Check Monotonicity
        if gp.monotonic_rho:
            kz_rho_DM_vec_temp = profs.get_prof('kz_rho_DM_vec', pop)
            if min(kz_rho_DM_vec_temp) < 0:
                gh.LOG(1,'Negative kz_rho_DM in gl_chi')
                raise ValueError('negative value in kz_rho_DM array')

        if gp.monotonic_nu:
            kz_nu_vec_temp = profs.get_prof('kz_nu_vec', pop)
            if min(kz_nu_vec_temp) < 0:
                gh.LOG(1,'Negative kz_nu_DM in gl_chi')
                raise ValueError('negative value in kz_nu array')

        #If monotonicity passed calculate chi2
        nudat    = gp.dat.nu[pop]
        nuerr    = gp.dat.nuerr[pop]+profs.hyper_nu  # adding hyperparam to error
        numodel  = profs.get_prof('nu_vec', pop)
        chi2_nu = chi2func(numodel, nudat, nuerr) #TEST [0:-1]
        gh.LOG(1, ' chi2_nu0 = ', chi2_nu)

        if not gp.chi2_nu_converged and not gp.plotting_flag:
            continue # with pop loop

        sigz2dat    = gp.dat.sigz2[pop]    # [km/s]
        sigz2err    = gp.dat.sigz2err[pop]+profs.hyper_sigz2  # [km/s]
        sigz2_model = profs.get_prof('sigz2_vec', pop)
        chi2_sigz2  = chi2func(sigz2_model, sigz2dat, sigz2err) # [1]
        if chi2_sigz2 == np.inf:
            print('chi2_sig has become infinite')
            pdb.set_trace()
        gh.LOG(1, '  chi2_sigz2  = ', chi2_sigz2)

        if gp.tilt:
            sigmaRzdat = gp.dat.tilt 
            sigmaRzerr = gp.dat.tilterr
            sigmaRz_model = profs.get_prof('sigmaRz_vec', pop)
            chi2_tilt = chi2func(sigmaRz_model, sigmaRzdat, sigmaRzerr)
            #print ('sigmaRz2dat:',sigmaRz2dat)
            #print ('sigmaRz2_model:',sigmaRz2_model)
            #print ('sigmaRz2err:',sigmaRz2err)
            chi2 = chi2_nu+chi2_sigz2+chi2_tilt
            #print ('chi2:',chi2,'chi2_tilt:',chi2_tilt)
        else:
            chi2 = chi2_nu+chi2_sigz2 

    # switch to chi2_sig calculation too, if converged on Sig
    if not gp.chi2_nu_converged:
        chi2 = chi2_nu*1.
        chi2 *= 10
        if chi2 < gp.chi2_switch:
            gp.chi2_switch_counter +=1
            print('chi2 less than switch found, ', gp.chi2_switch_counter, ' out of ', gp.chi2_switch_mincount, ' needed.')
        if gp.chi2_switch_counter>= gp.chi2_switch_mincount:
            gh.LOG(1, 'nu burn-in finished, switching on sigma')
            gp.chi2_nu_converged = True

        #if chi2 < gp.chi2_switch:
        #    pdb.set_trace()
        #    gh.LOG(1, 'nu burn-in finished, switching on sigma')
        #    gp.chi2_nu_converged = True

    return chi2
## \fn calc_chi2(profs)
# Calculate chi^2
# @param profs profiles for rho, M, nu_i, beta_i, sig_i, kap_i
