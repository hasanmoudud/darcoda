#!/usr/bin/python
# calculate density falloff of circular rings around center of mass
###################################################################

#start from data centered on COM already:
import sys
import pdb
import numpy as np
from pylab import *
import math
import gl_params as gp
import gr_params as gpr
from gl_helper import expDtofloat
from gl_class_files import *

for i in range(gpr.ncomp):
    print 'i = ',i
    print 'input: ',gpr.get_com_file(i)
    x,y,v = np.loadtxt(gpr.get_com_file(i),\
                           skiprows=1,usecols=(0,1,2),unpack=True) #[rcore], [rcore], [km/s]


    # calculate radius
    r = np.sqrt(x**2+y**2) #[rcore]

    # set number and size of (linearly spaced) bins
    rmin = 0. #[rcore]
    rmax = max(r) if gpr.rprior<0 else 1.0*gpr.rprior #[rcore]

    print 'rmax [rcore] = ', rmax
    sel = (r<rmax)
    x = x[sel]; y = y[sel]; v = v[sel] #[rcore]
    totmass = 1.*len(x) #[munit], munit = 1/star
    
    binlength = (rmax-rmin)/(1.*gpr.nbins) #[rcore]
    print 'binlength [rcore] = ', binlength
    binmin = np.zeros(gpr.nbins);  binmax = np.zeros(gpr.nbins)
    rbin = np.zeros(gpr.nbins)
    for k in range(gpr.nbins):
        binmin[k] = rmin+k*binlength #[rcore]
        binmax[k] = rmin+(k+1)*binlength #[rcore]
        rbin[k]   = binmin[k]+0.5*binlength #[rcore]

    #volume of a circular bin with dr=binlength
    vol = np.zeros(gpr.nbins)
    for k in range(gpr.nbins):
        vol[k] = np.pi*(binmax[k]**2-binmin[k]**2) # [rcore**2]

    # rs = gpr.rerror*np.random.randn(len(r))+r
    rs = r  #[rcore] # if no initial offset is whished

    print 'output: '
    print gpr.get_dens_file(i)
    de = open(gpr.get_dens_file(i),'w')
    print gpr.get_enc_mass_file(i)
    em = open(gpr.get_enc_mass_file(i),'w')

    print>>de,'r','nu(r)/nu(0)','error'
    print>>em,'r','M(<r)','error'

    #1000 iterations for getting random picked radius values
    n = 1000
    density = np.zeros((gpr.nbins,n))
    a       = np.zeros((gpr.nbins,n))
    for k in range(n):
        rsi = gpr.rerror*np.random.randn(len(rs))+rs #[rcore]
        for j in range(gpr.nbins):
            ind1 = np.argwhere(np.logical_and(rsi>binmin[j],rsi<binmax[j])).flatten() #[1]
            density[j][k] = (1.*len(ind1))/vol[j]*totmass # [munit/rcore**2]
            a[j][k] = 1.*len(ind1) #[1]

    dens0 = np.sum(density[0])/(1.*n) # [munit/rcore**2]
    print 'dens0 = ',dens0,'[munit/rcore**2]'
    crcore = open(gpr.get_params_file(i),'r')
    rcore = np.loadtxt(crcore, comments='#', skiprows=1, unpack=False)
    crcore.close()

    cdens = open(gpr.get_params_file(i),'a')
    print >> cdens, dens0          #[munit/rcore**2]
    print >> cdens, dens0/rcore**2 #[munit/pc**2]
    print >> cdens, totmass        #[munit]
    cdens.close()
    
    ab0   = np.sum(a[0])/(1.*n)       # [1]
    denserr0 = dens0/np.sqrt(ab0)     # [munit/rcore**2]

    p_dens  = np.zeros(gpr.nbins);  p_edens = np.zeros(gpr.nbins)

    for b in range(gpr.nbins):
        dens = np.sum(density[b])/(1.*n) #[munit/rcore**2]
        ab   = np.sum(a[b])/(1.*n)       #[1]
        denserr = dens/np.sqrt(ab)       #[munit/rcore**2]
        denserror = np.sqrt((denserr/dens0)**2+(dens*denserr0/(dens0**2))**2) #[1]
        if(math.isnan(denserror)):
            denserror = 0. #[1]
            ## [PS]: TODO: change bin sizes to include same number of
            ##             stars in each bin, not assigning wrong density as below
            p_dens[b] = p_dens[b-1]  #[1]
            p_edens[b]= p_edens[b-1] #[1]
        else:
            p_dens[b] = dens/dens0   #[1]
            p_edens[b]= denserror    #[1] #100/rbin would be artificial guess

    for b in range(gpr.nbins):
        print >> de,rbin[b],p_dens[b],p_edens[b] # [rcore], [dens0], [dens0]
        indr = (r<binmax[b])
        menclosed = 1.0*np.sum(indr)/totmass # /totmass for normalization to 1 at last bin #[totmass]
        merror = menclosed/np.sqrt(ab) # artificial menclosed/10 gives good approximation #[totmass]
        print >> em,rbin[b],menclosed,merror #[rcore], [totmass], [totmass]
        #TODO: check: take rbinmax for MCMC?
    de.close()
    em.close()

    ion(); subplot(111)
    print 'rbin = ',rbin
    print 'p_dens = ',p_dens
    print 'p_edens = ',p_edens

    plot(rbin,p_dens,'b',linewidth=3)
    lbound = p_dens-p_edens; lbound[lbound<1e-6] = 1e-6
    ubound = p_dens+p_edens; 
    fill_between(rbin,lbound,ubound,alpha=0.5,color='r')
    yscale('log')
    xlim([np.min(rbin),np.max(rbin)])
    ylim([1e-3,3.])#ylim([1e-6,2*np.max(p_dens)])
    # ylim([0,1])
    xlabel(r'$r [r_c]$')
    ylabel(r'$\nu(r)/\nu(0)$')
    # plt.legend(['\rho','\rho'],'lower left')
    # title(fil)
    # axes().set_aspect('equal')
    savefig(gpr.get_dens_png(i))
    if gpr.showplots:
        ioff(); show(); clf()

