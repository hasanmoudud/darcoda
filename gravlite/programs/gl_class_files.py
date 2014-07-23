#!/usr/bin/env ipython3

##
# @file
# class to generate all filenames, independent of which investigation

# (c) 2013 ETHZ, psteger@phys.ethz.ch

import os, pdb, sys, pickle
import numpy as np
import gl_helper as gh

def get_case(cas):
    ntracer = 0
    if cas == 1:
        ntracer = 3000
    elif cas == 2:
        ntracer = 10000
    return ntracer
## \fn get_case(cas)
# Set number of tracers to look at
# want to set ntracer = 3e3              # case 1
#             ntracer = 3e4              # case 2
# @param cas case number: 0 (3000 tracers, 10k tracers)


import os
import os.path
def newdir(bname):
    if not os.path.exists(bname):
        os.makedirs(bname)
    return
## \fn newdir(bname)
# create new directory
# @param bname path


class Files:
    # massfile[], nufile[], sigfile[], outname = Files(investigate)
    # we have the convention to use
    # pop==0 for all tracer populations together
    # pop==1 for first tracer population
    # pop==2 for second tracer population, and so on
    def __init__ (self, gp, timestamp=''):
        ## set which computer we are working on
        self.machine = ''
        ## set base directory, link version for short filenames
        self.shortdir = ''
        self.longdir = ''
        self.dir = ''
        ## relative path to the 'programs' directory
        self.progdir = ''
        self.modedir = ''
        self.set_dir(gp.machine, gp.case, gp.investigate) # 'darkside' or 'local'
        ## file with 2D summed masses
        self.massfiles = []
        ## file with analytic values for Walker models
        self.analytic = ''
        ## file with 2D surface density
        self.surfdenfiles = []
        ## files with tracer densities
        self.Sigfiles  = []
        ## files with velocity dispersions
        self.sigfiles = []
        ## files with centered positions and velocities for the tracer particles
        self.posvelfiles = []
        ## files for the fourth order moment of the LOS velocity
        self.kappafiles = [];

        ## [beta_star1, r_DM, gamma_star1, r_star1, r_a1, gamma_DM, rho0]
        self.params = []

        if gp.investigate == 'hern':
            self.set_hern(gp, timestamp)
        elif gp.investigate == 'walk':
            self.set_walk(gp, timestamp)
        elif gp.investigate == 'gaia':
            self.set_gaia(gp, timestamp)
        elif gp.investigate == 'triax':
            self.set_triax(gp, timestamp)
        elif gp.investigate == 'obs':
            self.set_obs(gp, timestamp)
        elif gp.investigate == 'discsim':
            self.set_discsim(gp, timestamp)
        elif gp.investigate == 'discmock':
            self.set_discmock(gp, timestamp)


        ## directory and basename of all output files
        if timestamp == '':
            import datetime
            bname = datetime.datetime.now().strftime("%Y%m%d%H%M")
        else:
            bname = timestamp
        self.outdir = self.shortdir+bname+'/'
        self.outname = bname

        # shorter dir names in Multinest (bound to <= 100 total)
        #os.system('ln -sf '+ self.dir+' '+self.modedir + str(gp.case))
        os.system('mkdir -p '+self.outdir)

        newdir(self.dir + 'M/')
        newdir(self.dir + 'Sigma/')
        newdir(self.dir + 'siglos/')
        newdir(self.dir + 'kappalos/')
        # create new pc2.save file for profile storage that is appended to during the run
        if timestamp == '':
            with open(self.outdir+'pc2.save', 'wb') as fi:
                pickle.dump(-1, fi) # dummy data, to get file written new

        return
    ## \fn __init__(self, gp)
    # constructor
    # @param gp parameters
    # @param timestamp = '' used for output analysis


    def set_dir(self, machine, case, inv):
        if machine == 'darkside':
            self.machine = '/home/ast/read/dark/gravlite/'
        elif machine == 'local':
            self.machine = '/home/psteger/sci/gravlite/'
        self.progdir = self.machine + 'programs/'
        self.modedir = self.machine + 'DT' + inv + '/'
        self.shortdir = self.modedir + str(case) + '/'
        return
    ## \fn set_dir(self, machine, case, inv)
    # set local directory
    # @param machine depending on which computer is used
    # @param case which special case in investigated
    # @param inv string of investigation

    
    def set_ntracer(self, cas):
        ntracer = get_case(cas)
        ## number of tracers
        self.ntracer = ntracer
        ## string of the same quantity
        self.nstr = str(ntracer)
        return self.ntracer, self.nstr
    ## \fn set_ntracer(self,cas)
    # set number of tracers
    # @param cas based on the case (3k, 30k tracers) we are working on
        

    def get_sim_name(self, gp):
        if gp.hern_dual == 1:
            simname = 'unit_hern_1_'
        elif gp.hern_dual == 2:
            simname = 'dual_unit_hern_1_'
        return simname
    ## \fn get_sim_name(self, gp)
    # get simulation names in the Hernquist case
    # @param gp global parameters

        
    def set_hern(self, gp, timestamp=''):
        self.dir = self.machine + 'DThern/'
        self.dir += timestamp + '/'
        sim = self.get_sim_name(gp)
        self.massfiles.append(self.dir+'M/'+sim+'M_0.txt')
        self.Sigfiles.append(self.dir+'Sigma/'+sim+'Sig_0.txt') # all comp.
        self.Sigfiles.append(self.dir+'Sigma/'+sim+'Sig_1.txt') # first comp.

        self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_0.txt') # all comp.
        self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_1.txt') # first comp.

        self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_0.txt') # all comp.
        self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_1.txt') # first comp.

        if gp.pops == 1:
            self.massfiles.append(self.dir+'M/'+sim+'M_2.txt')
            self.Sigfiles.append(self.dir+'Sigma/' +sim+'Sig_2.txt')
            self.sigfiles.append(self.dir+'/siglos/' +sim+'veldisplos_2.txt')
            self.kappafiles.append(self.dir+'/kappalos/' +sim+'kappalos_2.txt')
                
        elif gp.pops == 2: # before: _*_[1,2].txt
            self.Sigfiles.append(self.dir+'Sigma/'+sim+'Sig.txt') # all comp.
            self.Sigfiles.append(self.dir+'Sigma/'+sim+'Sig_'+self.nstr1+'_0.txt')
            self.Sigfiles.append(self.dir+'Sigma/'+sim+'Sig_0_'+self.nstr2+'.txt')
            
            self.sigfiles.append(self.dir+'/siglos/' +sim+'veldisplos_'+self.nstr1+'_'+nstr2+'.txt') # all comp
            self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_'+self.nstr1+'_0.txt')
            self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_0_'+self.nstr2+'.txt')
            
            self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_'+self.nstr1+'_0.txt')
            self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_0_'+self.nstr2+'.txt')
        
        return
    ## \fn set_hern(self, gp, timestamp)
    # set all filenames for Hernquist case
    # @param gp global parameters
    # @param timestamp for analysis


    def set_gaia(self, gp, timestamp=''):
        beta_star1 = 5; r_DM = 1000
        if gp.case == 1:
            gamma_star1=0.1; r_star1=100;  r_a1=100;    gamma_DM=1; rho0=0.064
        elif gp.case == 2:
            gamma_star1=0.1; r_star1=250;  r_a1=250;    gamma_DM=0; rho0=0.400
        elif gp.case == 3:
            gamma_star1=0.1; r_star1=250;  r_a1=np.inf; gamma_DM=1; rho0=0.064
        elif gp.case == 4:
            gamma_star1=0.1; r_star1=1000; r_a1=np.inf; gamma_DM=0; rho0=0.400
        elif gp.case == 5:
            gamma_star1=1.0; r_star1=100;  r_a1=100;    gamma_DM=1; rho0=0.064
        elif gp.case == 6:
            gamma_star1=1.0; r_star1=250;  r_a1=250;    gamma_DM=0; rho0=0.400
        elif gp.case == 7:
            gamma_star1=1.0; r_star1=250;  r_a1=np.inf; gamma_DM=1; rho0=0.064
        elif gp.case == 8:
            gamma_star1=1.0; r_star1=1000; r_a1=np.inf; gamma_DM=0; rho0=0.400

        self.params = [beta_star1, r_DM, gamma_star1, r_star1, r_a1, gamma_DM, rho0]


        AAA = gh.myfill(100*gamma_star1)  # 100
        BBB = gh.myfill(10*beta_star1)    # 050
        CCC = gh.myfill(100*r_star1/r_DM) # 100
        DDD = gh.myfill(100*r_a1/r_star1) # 100
        EEEE = {0: "core",                     
             1: "cusp"
             }[gamma_DM]                # core
        FFFF = gh.myfill(1000*rho0, 4)
        self.longdir = 'gs'+AAA+'_bs'+BBB+'_rcrs'+CCC+'_rarc'+DDD+'_'+EEEE+'_'+FFFF+'mpc3_df/'
        if gp.case == 9:
            self.longdir = 'data_h_rh2_rs05_gs10_ra0_b05n_10k/'
        elif gp.case == 10:
            self.longdir = 'data_c_rh4_rs175_gs10_ra0_b05n_10k/'
        self.dir = self.modedir + self.longdir
        self.dir += timestamp + '/'
        ## new variable to hold the .dat input file
        self.datafile = self.dir + 'dat'

        self.massfiles.append(self.dir+'M/M_0.txt')
        self.Sigfiles.append(self.dir+'Sigma/Sig_0.txt') # all comp.
        self.sigfiles.append(self.dir+'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir+'kappalos/kappalos_0.txt')

        self.massfiles.append(self.dir+'M/M_1.txt')
        self.Sigfiles.append(self.dir+'Sigma/Sig_1.txt') # first and only
        self.sigfiles.append(self.dir+'siglos/siglos_1.txt')
        self.kappafiles.append(self.dir+'kappalos/kappalos_1.txt')
    ## \fn set_gaia(self, gp, timestamp)
    # derive filenames from gaia case
    # @param gp global parameters
    # @param timestamp for analysis
        

    def set_walk(self, gp, timestamp=''):
        self.dir = self.machine + 'DTwalk/'
        if gp.case == 0:
            gamma_star1 =   0.1;    gamma_star2 =   1.0 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     = 1000.;    r_star2     = 1000. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 0 # 0 or 1
            rno         = 3

        elif gp.case == 1:
            gamma_star1 =   1.0;    gamma_star2 =   1.0 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     =  500.;    r_star2     = 1000. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 0 # core
            rno         = 2

        elif gp.case == 2:
            gamma_star1 =   1.0;    gamma_star2 =   1.0 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     =  500.;    r_star2     = 1000. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 1 # cusp
            rno         = 8

        elif gp.case == 4:
            gamma_star1 =   0.1;    gamma_star2 =   0.1 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     =  100.;    r_star2     =  500. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 1 # cusp
            rno         = 5

        elif gp.case == 5:
            gamma_star1 =   1.0;    gamma_star2 =   0.1 # 1. or 0.1
            beta_star1  =   5.0;    beta_star2  =   5.0 # fixed to 5
            r_star1     = 1000.;    r_star2     = 1000. # 500 or 1000
            r_a1        =   1.0;    r_a2        =   1.0
            gamma_DM    = 0 # core
            rno         = 6

            
        alpha_DM    = 1;    beta_DM     = 3;
        r_DM        = 1000                    # fixed to 1000pc

        import gl_helper as gh
        AAA = gh.myfill(100*gamma_star1)     # 100
        BBB = gh.myfill(10*beta_star1)       # 050
        CCC = gh.myfill(r_star1/10)          # 100
        DDD = gh.myfill(100*r_a1)            # 100 
        EEE = {0: "core",
             1: "cusp"
             }[gamma_DM]                     # core
        FFF = gh.myfill(100*gamma_star2)     # 010
        GGG = gh.myfill(10*beta_star2)       # 050
        HHH = gh.myfill(r_star2/10)          # 100
        III = gh.myfill(100*r_a2)            # 100
        JJJ = EEE                            # core
        NNN = gh.myfill(rno)                   # 003    # realization (1..10)

        self.longdir = "c1_"+AAA+"_"+BBB+"_"+CCC+"_"+DDD+"_"+EEE+"_c2_"+FFF+"_"+GGG+"_"+HHH+"_"+III+"_"+JJJ+"_"+NNN+"_6d/"
        self.dir = self.modedir + self.longdir
        self.dir += timestamp + '/'


        self.analytic = self.dir + 'samplepars'
        # print('analytic set to ', self.analytic)
        LINE = np.loadtxt(self.analytic, skiprows=0, unpack=False)
        rho0        = LINE[19] # read from the corresp. samplepars file
        self.params = [beta_star1, r_DM, gamma_star1, r_star1, r_a1, gamma_DM, rho0]
        
        for i in np.arange(gp.pops+1): # 0, 1, 2 for gp.pops=2
            self.massfiles.append(self.dir+'M/M_'+str(i)+'.txt')
            self.Sigfiles.append(self.dir+'Sigma/Sig_'+str(i)+'.txt')
            self.sigfiles.append(self.dir+'siglos/siglos_'+str(i)+'.txt')
            self.kappafiles.append(self.dir+'kappalos/kappalos_'+str(i)+'.txt')
        return
    ## \fn set_walk(self, gp, timestamp)
    # derive filenames from Walker&Penarrubia parameters
    # @param gp parameters
    # @param timestamp for analysis


    def set_triax(self, gp, timestamp=''):
        self.longdir = str(gp.case) + '/'
        self.dir = self.modedir + self.longdir
        self.dir += timestamp + '/'

        self.massfiles.append(self.dir + 'M/M_0.txt')
        self.Sigfiles.append(self.dir    + 'Sigma/Sig_0.txt')
        self.sigfiles.append(self.dir   + 'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir + 'kappalos/kappalos_0.txt')

        # first and only comp.
        self.massfiles.append(self.dir + 'M/M_0.txt')
        self.Sigfiles.append(self.dir    + 'Sigma/Sig_0.txt') 
        self.sigfiles.append(self.dir   + 'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir + 'kappalos/kappalos_0.txt')
        if gp.pops == 2:
            print('IMPLEMENT 2 tracer populations for triaxial dataset')
            sys.exit(1)
        return
    ## \fn set_triax(self, gp, timestamp)
    # set all parameters for working on the triaxial data
    # @param gp parameters
    # @param timestamp for analysis

    
    def set_obs(self, gp, timestamp=''):
        self.dir = self.machine + '/DTobs/'+str(gp.case)+'/'
        self.dir += timestamp + '/'
        for i in np.arange(gp.pops+1): # 0, 1, 2 for gp.pops=2
            self.massfiles.append(self.dir + 'M/M_'+str(i)+'.txt')
            self.Sigfiles.append(self.dir+'Sigma/Sig_'+str(i)+'.txt')
            self.sigfiles.append(self.dir+'siglos/siglos_'+str(i)+'.txt')
            self.kappafiles.append(self.dir+'kappalos/kappalos_'+str(i)+'.txt')
        return
    ## \fn set_obs(self, gp, timestamp)
    # set all variables in the case we work with Fornax observational data
    # @param gp
    # @param timestamp

    
    def populate_output_dir(self, gp):
        # copy only after data is read in!
        os.system('rsync -rl --exclude ".git" --exclude "doc" --exclude "__pycache__" ' + self.progdir + ' ' + self.outdir)
        os.system('rsync -rl --exclude "201*" ' + self.dir + ' ' + self.outdir) # copy data for later reference
        # rsync -r --exclude '.git' source target to exclude .git dir from copy
        return
    ## \fn populate_output_dir(self, gp)
    # copy data and program files to output directory, with timestamp
    # @param gp global parameters


    def get_scale_file(self, i):
        return self.dir+'scale_'+str(i)+'.txt'
    ## \fn get_scale_file(self, i)
    # return filename for storing scaling properties (half-light radius, ...)
    # @param i population number. 0: all pops, 1,2,n: component i


    def get_ntracer_file(self, i):
        return self.dir+'ntracer_'+str(i)+'.txt'
    ## \fn get_ntracer_file(self, i)
    # get filename with attached tracer information
        

    def set_discsim(self, gp, timestamp=''):
        # entry for "all components" as the first entry. Convention: 0. all 1. pop, 2. pop, 3. pop = background
        self.dir = self.machine + 'DTdiscsim/mwhr/'
        self.dir += timestamp + '/'

        # self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_stars.txt')
        # self.Sigfiles.append(self.dir + 'Sigma/mwhr_r8500_ang'+gp.patch+'_falloff_stars.txt') # again all components
        # self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvel_stars.txt') # all comp.
        # self.surfdenfiles.append(self.dir + 'surfden/mwhr_r8500_ang'+gp.patch+'_surfaceden.txt') # overall surface density?
        self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_stars.txt') # first comp.
        self.Sigfiles.append(self.dir + 'Sigma/mwhr_r8500_ang'+gp.patch+'_falloff_stars.txt') # first comp
        self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvel_stars.txt') # first comp.
        self.kappafiles.append(self.dir +  'kappalos/mwhr_r8500_ang'+gp.patch+'_kappa_stars.txt') # first comp.
        self.surfdenfiles.append(self.dir + 'surfden/mwhr_r8500_ang'+gp.patch+'_surfaceden.txt') # baryonic surface density 
        
        if gp.pops ==2:
            self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_dm.txt') # second comp.
            self.Sigfiles.append(self.dir + 'Sigma/mwhr_r8500_ang'+gp.patch+'_falloff_dm.txt') # second comp.
            self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvel_dm.txt') # second comp.
            self.kappafiles.append(self.dir +  'kappalos/mwhr_r8500_ang'+gp.patch+'_kappa_dm.txt') # second comp.
            self.surfdenfiles.append(self.dir + 'surfden/mwhr_r8500_ang'+gp.patch+'_surfacedenDM.txt') # DM surface density

        return
    ## \fn set_discsim(self, gp, timestamp='')
    # set all properties for disc case
    # @param gp global parameters
    # @param timestamp string YYYYMMDDhhmm

    
    def set_discmock(self, gp, timestamp=''):
        self.dir = self.machine + 'DTdiscmock/0/'
        self.dir += timestamp + '/'
        self.massfiles.append(self.dir+'M/M_0.txt')
        self.Sigfiles.append(self.dir+'nu/nu_0.txt') # all comp.
        self.sigfiles.append(self.dir+'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir+'kappalos/kappalos_0.txt')
        self.massfiles.append(self.dir+'M/M_1.txt')
        self.Sigfiles.append(self.dir+'nu/nu_1.txt') # all comp.
        self.sigfiles.append(self.dir+'siglos/siglos_1.txt')
        self.kappafiles.append(self.dir+'kappalos/kappalos_1.txt')
        if gp.pops == 2:
            self.massfiles.append(self.dir+'M/M_2.txt')
            self.Sigfiles.append(self.dir+'nu/nu_2.txt') # all comp.
            self.sigfiles.append(self.dir+'siglos/siglos_2.txt')
            self.kappafiles.append(self.dir+'kappalos/kappalos_2.txt')

        return
    ## \fn set_discmock(self, gp, timestamp='')
    # set all properties if looking at simple disc
    # @param gp global parameters
    # @param timestamp string YYYYMMDDhhmm
        

    def get_outfiles(self):
        pre = self.outdir # + self.outname + '.'
        outplot = pre + 'png'
        outdat  = pre + 'dat'
        outtxt  = pre + 'txt'
        return outplot, outdat, outtxt
    ## \fn get_outfiles(self)
    # get all output filenames
        

    def get_outpng(self):
        pre = self.outdir # + self.outname + '.'
        return pre + 'png'
    ## \fn get_outpng(self)
    # get output filename for png picture
        

    def get_outdat(self):
        pre = self.outdir # + self.outname + '.'
        return pre + 'dat'
    ## \fn get_outdat(self)
    # get output filename for data

        
    def get_outtxt(self):
        pre = self.outdir # + self.outname + '.'
        return pre + 'txt'
    ## \fn get_outtxt(self)
    # get output filename for ASCII output

    def __repr__(self):
        return "Files: "+self.dir
    ## \fn __repr__(self)
    # string representation

      

## \class Files
# Common base class for all filename sets