#!/usr/bin/env python3

##
# @file
# class to generate all filenames, independent of which investigation

# (c) 2013 ETHZ, psteger@phys.ethz.ch

import os, pdb
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


import os; import os.path
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
        self.nufiles  = []
        ## files with velocity dispersions
        self.sigfiles = []
        ## files with centered positions and velocities for the tracer particles
        self.posvelfiles = []
        ## files for the fourth order moment of the LOS velocity
        self.kappafiles = [];
        ## [beta_star1, r_DM, gamma_star1, r_star1, r_a1, gamma_DM, rho0]
        self.params = []

        if gp.investigate == 'hern':
            self.set_hern(timestamp)
        elif gp.investigate == 'walk':
            self.set_walk(gp, timestamp)
        elif gp.investigate == 'gaia':
            self.set_gaia(timestamp)
        elif gp.investigate == 'triax':
            self.set_triax(gp, timestamp)
        elif gp.investigate == 'obs':
            self.set_obs(gp, timestamp)
        elif gp.investigate == 'discsim':
            self.set_discsim(timestamp)
        elif gp.investigate == 'discmock':
            self.set_discmock(timestamp)
        self.create_dirs()

        ## directory and basename of all output files
        self.outdir, self.outname = self.get_outname()
        return
    ## \fn __init__(self, gp)
    # constructor
    # @param gp parameters
    # @param timestamp = '' used for output analysis

    def create_dirs(self):
        newdir(self.dir + 'enclosedmass/')
        newdir(self.dir + 'nu/')
        newdir(self.dir + 'siglos/')
        newdir(self.dir + 'kappalos/')
    ## \fn create_dirs(self)
    # mkdir for all data dirs, not in gr_params anymore

    
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
        

    def get_sim_name(self):
        if gp.sim == 1:
            simname = 'unit_hern_1_'
        elif gp.sim == 2:
            simname = 'dual_unit_hern_1_'
        return simname
    ## \fn get_sim_name(self)
    # get simulation names in the Hernquist case

        
    def set_hern(self, timestamp=''):
        self.dir = self.machine + 'DThern/'
        self.dir += timestamp + '/'
        sim = self.get_sim_name()
        self.massfiles.append(self.dir+'enclosedmass/'+sim+'enclosedmass_0.txt')
        self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm_0.txt') # all comp.
        self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm_1.txt') # first comp.

        self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_0.txt') # all comp.
        self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_1.txt') # first comp.

        self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_0.txt') # all comp.
        self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_1.txt') # first comp.

        if gp.pops == 1:
            self.massfiles.append(self.dir+'enclosedmass/'+sim+'enclosedmass_2.txt')
            self.nufiles.append(self.dir+'densityfalloff/' +sim+'falloffnotnorm_2.txt')
            self.sigfiles.append(self.dir+'/siglos/' +sim+'veldisplos_2.txt')
            self.kappafiles.append(self.dir+'/kappalos/' +sim+'kappalos_2.txt')
                
        elif gp.pops == 2: # before: _*_[1,2].txt
            self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm.txt') # all comp.
            self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm_'+self.nstr1+'_0.txt')
            self.nufiles.append(self.dir+'densityfalloff/'+sim+'falloffnotnorm_0_'+self.nstr2+'.txt')
            
            self.sigfiles.append(self.dir+'/siglos/' +sim+'veldisplos_'+self.nstr1+'_'+nstr2+'.txt') # all comp
            self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_'+self.nstr1+'_0.txt')
            self.sigfiles.append(self.dir+'siglos/'+sim+'veldisplos_0_'+self.nstr2+'.txt')
            
            self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_'+self.nstr1+'_0.txt')
            self.kappafiles.append(self.dir+'kappalos/'+sim+'kappalos_0_'+self.nstr2+'.txt')
        
        return
    ## \fn set_hern(self, timestamp)
    # set all filenames for Hernquist case
    # @param timestamp for analysis


    def set_gaia(self, timestamp=''):
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
        self.dir = self.modedir + self.longdir
        self.dir += timestamp + '/'
        ## new variable to hold the .dat input file
        self.datafile = self.dir + 'dat'

        self.massfiles.append(self.dir+'enclosedmass/enclosedmass_0.txt')
        self.nufiles.append(self.dir+'nu/nunotnorm_0.txt') # all comp.
        self.sigfiles.append(self.dir+'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir+'kappalos/kappalos_0.txt')

        self.massfiles.append(self.dir+'enclosedmass/enclosedmass_1.txt')
        self.nufiles.append(self.dir+'nu/nunotnorm_1.txt') # first and only
        self.sigfiles.append(self.dir+'siglos/siglos_1.txt')
        self.kappafiles.append(self.dir+'kappalos/kappalos_1.txt')
    ## \fn set_gaia(self, timestamp)
    # derive filenames from gaia case
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
            self.massfiles.append(self.dir + 'enclosedmass/enclosedmass_'+str(i)+'.txt')
            self.nufiles.append(self.dir+'nu/nunotnorm_'+str(i)+'.txt')
            self.sigfiles.append(self.dir+'siglos/siglos_'+str(i)+'.txt')
            self.kappafiles.append(self.dir+'kappalos/kappalos_'+str(i)+'.txt')
        return
    ## \fn set_walk(self, gp, timestamp)
    # derive filenames from Walker&Penarrubia parameters
    # @param gp parameters
    # @param timestamp for analysis


    def set_triax(self, gp, timestamp=''):
        if gp.case == 0:           # core
            casename = 'StarsInCore'
        elif gp.case == 1:
            casename = 'StarsInCusp'
        if gp.projcase == 1:            # along X
            proj = 'X'
        elif gp.projcase == 2:          # along Y
            proj = 'Y'
        elif gp.projcase == 3:          # along Z
            proj = 'Z'
        elif gp.projcase == 4:          # along intermediate axis
            proj = 'I'
        self.longdir = casename + proj + '/'
        self.dir = self.modedir + self.longdir
        self.dir += timestamp + '/'


        self.massfiles.append(self.dir + 'enclosedmass/enclosedmass_0.txt')
        self.nufiles.append(self.dir    + 'nu/nunotnorm_0.txt')
        self.sigfiles.append(self.dir   + 'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir + 'kappalos/kappalos_0.txt')

        # first and only comp.
        self.massfiles.append(self.dir + 'enclosedmass/enclosedmass_0.txt')
        self.nufiles.append(self.dir    + 'nu/nunotnorm_0.txt') 
        self.sigfiles.append(self.dir   + 'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir + 'kappalos/kappalos_0.txt')
        if gp.pops == 2:
            print('IMPLEMENT 2 tracer populations for triaxial dataset')
            pdb.set_trace()
        return
    ## \fn set_triax(self, gp, timestamp)
    # set all parameters for working on the triaxial data
    # @param gp parameters
    # @param timestamp for analysis

    
    def set_obs(self, gp, timestamp=''):
        self.dir = self.machine + '/DTobs/'+gp.case+'/'
        self.dir += timestamp + '/'
        self.massfiles.append(self.dir+'enclosedmass/enclosedmass_0.txt')
        self.nufiles.append(self.dir+'nu/nunotnorm_0.txt')
        self.sigfiles.append(self.dir+'siglos/siglos_0.txt')
        self.kappafiles.append(self.dir+'kappalos/kappalos_0.txt')
        if gp.pops == 1:
            self.massfiles.append(self.dir+'enclosedmass/enclosedmass_0.txt')
            self.nufiles.append(self.dir+'nu/nunotnorm_0.txt') # first and only comp.
            self.sigfiles.append(self.dir+'siglos/siglos_0.txt')
            self.kappafiles.append(self.dir+'kappalos/kappalos_0.txt')
        if gp.pops == 2:
            self.massfiles.append(self.dir+'enclosedmass/enclosedmass_1.txt')
            self.nufiles.append(self.dir+'nu/nunotnorm_1.txt') # first comp.
            self.sigfiles.append(self.dir+'siglos/siglos_1.txt')
            self.kappafiles.append(self.dir+'kappalos/kappalos_1.txt')

            self.massfiles.append(self.dir+'enclosedmass/enclosedmass_2.txt')
            self.nufiles.append(self.dir+'nu/nunotnorm_2.txt') # second comp.
            self.sigfiles.append(self.dir+'siglos/siglos_2.txt')
            self.kappafiles.append(self.dir+'kappalos/kappalos_2.txt')
        return
    ## \fn set_obs(self, gp, timestamp)
    # set all variables in the case we work with Fornax observational data
    # @param gp
    # @param timestamp

    
    def get_outname(self):
        import datetime
        bname = datetime.datetime.now().strftime("%Y%m%d%H%M")
        return self.shortdir+bname+'/', bname
    ## \fn get_outname(self)
    # determine output directory and filenames, create dir
    # @return ouput directory, base of filenames


    def create_output_dir(self, gp):
        # shorter dir names in Multinest (bound to <= 100 total)
        os.system('ln -sf '+ self.dir+' '+self.modedir + str(gp.case))
        os.system('mkdir -p '+self.outdir)
        return
    ## \fn create_output_dir(self, gp)
    # create output directory and copy the current program files into it
    # @param gp global parameters


    def populate_output_dir(self, gp):
        # copy only after data is read in!
        os.system('rsync -rl --exclude ".git" --exclude "__pycache__" ' + self.progdir + ' ' + self.outdir)
        os.system('rsync -rl --exclude "201*" ' + self.dir + ' ' + self.outdir) # copy data for later reference
        # rsync -r --exclude '.git' source target to exclude .git dir from copy
        return
    ## \fn populate_output_dir(self, gp)
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
        

    def set_discsim(self):
        # entry for "all components" as the first entry. Convention: 0. all 1. pop, 2. pop, 3. pop = background
        self.dir = self.machine + 'DTdiscsim/mwhr/'
        # self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_stars.txt')
        # self.nufiles.append(self.dir + 'nu/mwhr_r8500_ang'+gp.patch+'_falloff_stars.txt') # again all components
        # self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvel_stars.txt') # all comp.
        # self.surfdenfiles.append(self.dir + 'surfden/mwhr_r8500_ang'+gp.patch+'_surfaceden.txt') # overall surface density?
        self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_stars.txt') # first comp.
        self.nufiles.append(self.dir + 'nu/mwhr_r8500_ang'+gp.patch+'_falloff_stars.txt') # first comp
        self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvel_stars.txt') # first comp.
        self.kappafiles.append(self.dir +  'kappalos/mwhr_r8500_ang'+gp.patch+'_kappa_stars.txt') # first comp.
        self.surfdenfiles.append(self.dir + 'surfden/mwhr_r8500_ang'+gp.patch+'_surfaceden.txt') # baryonic surface density 
        
        if gp. pops ==2:
            self.posvelfiles.append(self.dir + 'sim/mwhr_r8500_ang'+gp.patch+'_dm.txt') # second comp.
            self.nufiles.append(self.dir + 'nu/mwhr_r8500_ang'+gp.patch+'_falloff_dm.txt') # second comp.
            self.sigfiles.append(self.dir +  'siglos/mwhr_r8500_ang'+gp.patch+'_dispvel_dm.txt') # second comp.
            self.kappafiles.append(self.dir +  'kappalos/mwhr_r8500_ang'+gp.patch+'_kappa_dm.txt') # second comp.
            self.surfdenfiles.append(self.dir + 'surfden/mwhr_r8500_ang'+gp.patch+'_surfacedenDM.txt') # DM surface density

        return
    ## \fn set_discsim(self)
    # set all properties for disc case

    
    def set_discmock(self):
        self.dir = self.machine + 'DTdiscmock/'
        return
    ## \fn set_discmock(self)
    # set all properties if looking at simple disc (generated on the fly, no data input files needed)
        

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

        

## \class Files
# Common base class for all filename sets