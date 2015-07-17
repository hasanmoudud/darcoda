#!/usr/bin/env ipython3

##
# @file
# all parameters for the gravimage MCMC, gaia investigation

# (c) 2013 ETHZ Pascal S.P. Steger

import numpy as np
import pdb
import gl_helper as gh
#import socket
#import getpass

def check_investigate(inv):
    if inv == 'discmock': return True
    if inv == 'discsim': return True
    raise Exception('wrong investigative case in gl_params')
    return False

class Params():
    def __init__(self, timestamp = '', investigate = '', case = -1):

        # Set machine and user variables
        # ----------------------------------------------------------------------
        self.machine, dummy = gh.detect_machine()


        # Set investigation and geometry
        # ----------------------------------------------------------------------
        if investigate != '':
            self.investigate = investigate
        else:
            self.investigate  = 'simplenu' # determine which data set to work on
                                  # 'discmock': set up simple model for disc
                                  # 'discsim': read in disc simulation
        self.geom = 'disc'

        #check_investigate(self.investigate)
        self.case = 0 # used in spherical case
        self.ntracer_pops = 1 # number of stellar tracer populations
                      # if changed: set getnewdata=True!


        # debug options
        # ----------------------------------------------------------------------
        self.checksig = False # debug sig calculation?
        self.debug = False # stop at wrong sanitazion?


        # data and analysis options
        # ----------------------------------------------------------------------
        self.getnewdata = True  # get new data computed from
                                # observations before burn-in
        self.getnewpos  = True  # redo the first data conversion step


        ##Popn 1 1E4
        #self.external_data_file= ['/simplenu/simple_1e4nu_sigz_raw.dat']
        ##self.external_data_file_tilt = ['/simplenu/simple_tilt_1e6nu_sigz_raw.dat']

        ##Popn 2 1E4
        #self.external_data_file= ['/simplenu/simple2_1e6nu_sigz_raw.dat']
        ##self.external_data_file_tilt = ['/simplenu/simple2_tilt_1e6nu_sigz_raw.dat']

        #Popn 1 & 2 1E4
        #self.external_data_file= ['/simplenu/simple_1e6nu_sigz_raw.dat', '/simplenu/simple2_1e6nu_sigz_raw.dat']
        #self.external_data_file_tilt = ['/simplenu/simple_tilt_1e6nu_sigz_raw.dat', '/simplenu/simple2_tilt_1e6nu_sigz_raw.dat']


        ##Popn 1 1E6
        #self.external_data_file= ['/simplenu/simple_1e6nu_sigz_raw.dat']
        ##self.external_data_file_tilt = ['/simplenu/simple_tilt_1e6nu_sigz_raw.dat']

        #Popn 2 1E6
        self.external_data_file= ['/simplenu/simple2_1e6nu_sigz_raw.dat']


        ##Popn 1 & 2 1E6
        #self.external_data_file= ['/simplenu/simple_1e6nu_sigz_raw.dat', '/simplenu/simple2_1e6nu_sigz_raw.dat']
        #self.external_data_file_tilt = ['/simplenu/simple_tilt_1e6nu_sigz_raw.dat', '/simplenu/simple2_tilt_1e6nu_sigz_raw.dat']

        ##Pop 2 1E6 with tilt
        #self.external_data_file = ['/simplenu/simple2_tilt_1e6nu_sigz_raw.dat']
        #self.external_data_file_tilt= ['/simplenu/simple2_tilt_1e6nu_sigRz_raw.dat']

        #self.external_data_file= ['/simplenu/simplenu_sigz_raw.dat'#_sdz_p05_sdvz_5.dat']
        #self.external_data_file= ['/simplenu/simple_1e6nu_sigz_raw.dat']
        #self.external_data_file= ['/simplenu/simple2_1e6nu_sigz_raw.dat']
        #self.external_data_file= ['/simplenu/simple2_tilt_1e6nu_sigz_raw.dat']
        #self.external_data_file= ['/simplenu/simple2_1e6nu_sigz_raw.dat']
        #self.external_data_file= ['/simplenu/simple2_tilt_1e6nu_sigz_raw.dat']
        #self.external_data_file= ['/simplenu/simple2_dd_1e6nu_sigz_raw.dat']
        #self.external_data_file= ['/simplenu/simple2_bdd_tilt_1e6nu_sigz_raw.dat']

        self.dd_data = False
        #self.dd_data = False  # if we are to plot dd analytics or not

        #self.external_data_file_tilt= ['/simplenu/simple2_bdd_tilt_1e6nu_sigRz_raw.dat']

        #self.external_data_file_tilt = ['/simplenu/simple_tilt_1e6nu_sigz_raw.dat']

        #self.data_z_cut = 1.2  # [kpz] only use (& bin) data up to this z limit
        self.data_z_cut = 2.4  # (set > data z_max to use all avaiable data)

        self.tilt = False   # If also modelling the tilt

        #self.darkmattermodel = 'const_dm' # const_dm = const DM dens in z
        #self.darkmattermodel = 'kz_dm'  # kz_dm = kz parameterization of DM
        self.darkmattermodel = 'ConstPlusDD' # constant DM + DM disc component

        self.binning = 'consttr' # 'linspace', 'logspace', 'consttr': binning of particles
        #self.binning = 'linspace' # 'linspace', 'logspace', 'consttr': binning of particles
        self.nbins = 20   # Number of bins to split tracer stars into
        self.nrhonu = self.nbins + 1 # Number of points where rho and nu parameters will be set,
                                   # e.g. bin centres, plus zC=0

        #------------------------
        self.TheoryData = False   # If true using theoretical bin values as indata
        self.hyperparams = False  # Use hyperparameters, 2 params, range (0.1->10)*meanerr
        #Dark matter options
        self.adddarkdisc = False  # for disc mock case: add a dark disc?
        # self.adddarkdisc is currently not used !

        #Baryon options
        self.baryonmodel = 'simplenu_baryon' #set baryon model
                                             # none = all mass in DM
                                    # setting baryonmodel == 'none' not possible without major rewrite
                                    # simplenu_baryon = model used to generate simplenu mock data
        self.nbaryon_pops = 1 # Number of baryon populations to look at
                                    # =0 if doing simple mass model (eg DM profile describes
                                    # all mmass)
        self.nbaryon_params = 2 # Number of parameters to describe baryon population
                                    #  simplenu_baryon = 2
                                    #  Holmberg & Flynn = ?
                                    #  with baryon observational information = nrho
        self.ntilt_params = 3  # Number of parameters used to describe tilt

        self.scan_rhonu_space = False #Search directly in rho or nu space, i.e. no kr parametrization
        if self.scan_rhonu_space:
            self.nrhonu = self.nbins #Param count will be rho_C + rho_bins

        # Parameters escribing the underlying baryonic model and the mock data
        # This is assuming baryonmodel = simplenu_baryon above, rewrite required if this is changed.

        #Total dimensions count
        if self.darkmattermodel == 'kz_dm':
            self.ndim = self.ntracer_pops + (1+self.ntracer_pops)*(self.nrhonu + 1) + self.nbaryon_pops*self.nbaryon_params
                # Constant C from sigma_z calculation (one for each tracer pop), (nrho + 1) params for rho (nrho
                # points for kz_rho, plus central density of rho, eg rho_C), similarly
                # (nrho +1)  params for tracer populations nu, plus the number of params for all baryon pops
        elif self.darkmattermodel == 'const_dm':
            self.ndim = self.ntracer_pops + 1 + (self.ntracer_pops)*(self.nrhonu + 1) + self.nbaryon_pops*self.nbaryon_params
                # Constant C from sigma_z calculations (one for each tracer pop), 1 for constant rho density,
                # (nrhonu + 1) for kz_nu and nu_C for each tracer popn, plus baryon params

        elif self.darkmattermodel == 'ConstPlusDD':
            self.ndim =  self.ntracer_pops + 3 + (self.ntracer_pops)*(self.nrhonu + 1) + self.nbaryon_pops*self.nbaryon_params
                # Constant C from sigma_z calculations (one for each tracer pop), 1 for constant rho density, 2 for dark disk,
                # (nrhonu + 1) for kz_nu and nu_C for each tracer popn, plus baryon params

        if self.hyperparams:
            self.ndim += 2

        if self.tilt:
            self.ndim += self.ntilt_params * self.ntracer_pops

        self.z_err_measurement = 0.05 # Measurement error on z, fraction, eg 0.05 = 5%
        self.vz_SDerr_meas = 5.  # Measurement error on vz, [km s^-1]
        self.mc_err_N_iters = int(100) #Number of iterations to perform when doing MC error estimation


        # Priors
        # ----------------------------------------------------------------------
        # Limits for central densities (z=0)
        self.rho_C_max = 1.0E8  #Msun kpc^-3 for either DM or baryons (cf rho_b = 0.0914 Msun pc^-3, Flynn+ 2006)
        self.rho_C_min = 1.0E6 #Msun pc^-3
        self.rho_C_prior_type = 'log' #log, linear, gaussian
        self.nu_C_max = 0.0 # no. stars pc^-3, full value calculated in external_data
        self.nu_C_min = 10.0 # no. stars pc^-3
        self.nu_C_prior_type = 'log'

        # Limits for central kz values (z=0)
        self.kz_rho_C_max = 5.0
        self.kz_rho_C_min = -5.0 #SS
        self.kz_nu_C_max = 5.#20.0
        self.kz_nu_C_min = -5.0 #SS

        # Maximum kz_slope (=dk/dz)
        #self.max_kz_slope = 10.0
        self.max_kz_slope = 5.0

        # Limits for sigz central value
        self.sigz_C_max = 50.
        self.sigz_C_min = 5.

        # Monotonicity priors
        self.monotonic_rho = False    # mono-prior on rho(z)
        self.monotonic_nu = False # mono-prior on nu(z)

        # kz selection scheme
        self.kz_rho_selection = 'gaussian'
        self.kz_nu_selection = 'tophat'

        # Log or linear priors for rhonu scanning
        self.prior_type_rho = 'gaussian' # 'log' or 'linear'
        self.prior_type_nu = 'gaussian' # 'log' or 'linear'

        # Simplenu Baryon model priors
        self.simplenu_baryon_K_max = 1650  #JR model has K = 1500.
        self.simplenu_baryon_K_min = 1350
        self.simplenu_baryon_D_max = 0.2  #JR model has D = 0.18
        self.simplenu_baryon_D_min = 0.16
        #self.simplenu_baryon_K_max = 2000  #1600 #1700. #JR model has K = 1500.
        #self.simplenu_baryon_K_min = 1000  #1400 #1300.
        #self.simplenu_baryon_D_max = 0.24  #0.20 #0.5 #JR model has D = 0.18
        #self.simplenu_baryon_D_min = 0.12  #0.16 #0.05

        # Simplenu DM disc model priors
        self.simplenu_dm_K_max = 1500.  #JR model has K = 300.
        self.simplenu_dm_K_min = 0.
        self.simplenu_dm_D_max = 3.5  #JR model has D = 2.5
        self.simplenu_dm_D_min = 1.5

        # Tilt priors
        self.tilt_A_max = -0.005  # simple2 mock has A = -0.0087
        self.tilt_A_min = -0.012
        self.tilt_n_max = 1.9    # simple2 mock has n = 1.44
        self.tilt_n_min = 1.
        self.tilt_R_max = 3.5     # simple2 mock has R = 2.5
        self.tilt_R_min = 1.5


        # MultiNest options
        # ----------------------------------------------------------------------
        self.map_priors = False
        # Set number of terms for enclosedmass+tracer+anisotropy bins
        # = model parameters:
        self.chi2_nu_converged = False # first converge on Sig if set to False
        self.chi2_switch = 100. # if chi2*10 < chi2_switch, add chi2_sig
        self.chi2_switch_mincount = 0. # demand that this number of profiles with
                                        # chi2<chi2_switch are found before adding chi2_sig
        self.chi2_switch_counter = 0. # start the counter at 0

        # live points, > ndim, < 2^ndim, about number of
        # ellipsoids in phase space to be found
        self.nlive = 100*self.ndim
        self.err = 1e300    # chi^2 for models which are impossible

        #fraction of profiles to save, set <0 for no profile saving
        self.save_fraction = -1.0

        #Plotting flag
        self.plotting_flag = False

        # filesystem-related
        # ----------------------------------------------------------------------
        import import_path as ip
        ip.set_geometry(self.geom, self.machine) # load spherical or
                                                 # disc version
                                                 # of the code
        import gl_class_files
        self.files = gl_class_files.Files(self, timestamp)
        from gl_data import Datafile
        self.dat = Datafile()


        # global arrays
        # ----------------------------------------------------------------------
        self.z_bincenters = np.array([]) # [pc] holds the bin centers, H Silverwood 21/11/14
        self.z_binmins = np.array([])
        self.z_binmaxs = np.array([])
        self.z_all_pts = np.array([]) # [pc] holds [zC = 0, z_bin_centers]

        # Global constants
        self.Rsun = 8.  # [kpc]  Sun's distance to galactic center

    ## \fn __init__(self, timestamp = '')
    # set up all parameters used in the course of the MultiNest run,
    # and the analysis routines in plot_multinest @param timestamp =
    # '', for output


    def __repr__(self):
        return "Params: "+self.files.dir
    ## \fn __repr__(self)
    # string representation for ipython
