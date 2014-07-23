#!/usr/bin/env ipython3

##
# @file
# calculate surface mass density falloff of circular rings around center of mass
# for triaxial systems
# TODO: enable ellipsoidal bins

# (c) 2013 Pascal S.P. Steger


import sys, pdb
import numpy as np
import gr_params as gpr
import gl_file as gfile
import gl_helper as gh
from gl_helper import expDtofloat, bin_r_linear, bin_r_log, bin_r_const_tracers


def run(gp):
    print('input: ',gpr.get_com_file(0))
    # start from data centered on COM already:
    x,y,v = np.loadtxt(gpr.get_com_file(0),\
                       skiprows=1,usecols=(0,1,2),unpack=True) #[Rscalei], [Rscalei], [km/s]

    for comp in range(2):
        # calculate 2D radius on the skyplane
        R = np.sqrt(x**2+y**2) # [Rscalei]

        # set number and size of bins
        Rmin = 0. # [rscale]
        Rmax = max(R) if gp.maxR < 0 else float(gp.maxR)   # [Rscale0]
        sel = (R * Rscalei < Rmax * Rscale0)
        x = x[sel]; y = y[sel]; v = v[sel] #[rscale]
        totmass = 1.*len(x) #[munit], munit = 1/star

        if gpr.lograd:
            # space logarithmically in radius
            Binmin, Binmax, Rbin = bin_r_log(Rmax/gp.nipol, Rmax, gp.nipol) # [Rscale0]
        elif gp.consttr:
            Binmin, Binmax, Rbin = bin_r_const_tracers(R, len(R)/gp.nipol) # [Rscale0]
        else:
            Binmin, Binmax, Rbin = bin_r_linear(Rmin, Rmax, gp.nipol) # [Rscale0]

        Vol = gpr.volume_circular_ring(Binmin, Binmax, gp)

        # rs = gpr.Rerr*np.random.randn(len(r))+r
        Rs = R  # [Rscale] # if no initial offset is whished

        tr = open(gp.files.get_ntracer_file(0),'w')
        print(totmass, file=tr)
        tr.close()

        de, em, sigfil, kapfil = gfile.write_headers_2D(gp, 0)

        # 30 iterations for getting random picked radius values
        Density = np.zeros((gp.nipol,gpr.n))
        tpb       = np.zeros((gp.nipol,gpr.n))
        for k in range(gpr.n):
            Rsi = gh.add_errors(Rs, gpr.Rerr) # [Rscalei]
            for j in range(gp.nipol):
                ind1 = np.argwhere(np.logical_and(Rsi * Rscalei >= Binmin[j] * Rscale0,\
                                                  Rsi * Rscalei <  Binmax[j] * Rscale0)).flatten() # [1]
                Density[j][k] = float(len(ind1))/Vol[j]*totmass # [munit/Rscale0^2]
                tpb[j][k] = float(len(ind1)) #[1]

        Dens0 = np.sum(Density[0])/float(gpr.n) # [Munit/Rscale0^2]
        Dens0pc = Dens0/Rscale0**2 # [Munit/pc^2]
        gfile.write_density(gp.files.get_scale_file(0), Dens0pc, totmass)

        tpbb0   = np.sum(tpb[0])/float(gpr.n)     # [1]
        Denserr0 = Dens0/np.sqrt(tpbb0)       # [Munit/rscale^2]

        p_dens  = np.zeros(gp.nipol)
        p_edens = np.zeros(gp.nipol)

        for b in range(gp.nipol):
            Dens = np.sum(Density[b])/float(gpr.n) # [Munit/rscale^2]
            tpbb = np.sum(tpb[b])/float(gpr.n)       # [1]
            Denserr = Dens/np.sqrt(tpbb)       # [Munit/rscale^2]
            if(np.isnan(Denserr)):
                p_dens[b] = p_dens[b-1]  # [1]
                p_edens[b]= p_edens[b-1] # [1]
            else:
                p_dens[b] = Dens/Dens0   # [1]
                p_edens[b]= Denserr/Dens0    # [1] #100/rbin would be artificial guess

        for b in range(gp.nipol):
            print(Rbin[b], Binmin[b], Binmax[b], p_dens[b], p_edens[b], file=de) # [rscale], [dens0], [dens0]
            indr = (R < Binmax[b])
            menclosed = float(np.sum(indr))/totmass
             # /totmass for normalization to 1 at last bin #[totmass]
            merr = menclosed/np.sqrt(tpbb) # artificial menclosed/10 gives good approximation #[totmass]
            print(Rbin[b], Binmin[b], Binmax[b], menclosed, merr, file=em)
            # [rscale], [totmass], [totmass]
        de.close()
        em.close()


        if gpr.showplots:
            gpr.show_plots_dens_2D(0, Rbin, p_dens, p_edens, Dens0pc)


if __name__ == '__main__':
    gpr.showplots = True
    import gl_params
    gp = gl_params.Params()
    run(gp)