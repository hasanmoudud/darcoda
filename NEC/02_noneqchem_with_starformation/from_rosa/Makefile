# take a choice: number of dimensions:  [1,2,3]
NDIM = 3

# take a choice: number of bytes for real numbers, real*NPRE: [4,8] (up to level10: 4, up to 21: 8)
NPRE = 8

# take a choice: solver
SOLVER = hydro

# take a choice: serial vs MPI execution
## serial:
#FC = ifort
F90 = ftn
#LIBMPI = -DWITHOUTMPI

# Compilation time parameters..
NVECTOR = 64   # for gfortran



# take a choice: normal or with NONEQCHEM
## normal hydro only:
# NVAR = 6
# DNEC =
# EXEC = ramses
# PATCH =

## with NONEQCHEM:
NVAR = 15
DNEC = -DNONEQCHEM
EXEC = ramsesnec
PATCH = ../patch/noneqchem/




# take a choice: normal or debugging
## normal:
DFLAGS = -O3 -hfp3 -cpp # -eZ (for ftn cpp preprocessor) # -O3 #-r$(NPRE) #not valid for ifort
# eZ is for preprocessing (=> *.i) and compiling (=> *.o) of files with Cray Fortran ftn
# cpp is for inclusion of preprocessing with ifort
# choose one of them

## debugging:
#DFLAGS = -O0 -g -traceback -cpp -r$(NPRE) -fpe0 -ftrapuv -gen-interfaces -check -warn errors -warn interfaces -r$(NPRE)

# hilbert: up to level 10, can have NPRE=4, up to level 21, can have NPRE=8, above need :
HILBERT = QUADHILBERT
# for convergence





#############################################################################

FFLAGS = $(DFLAGS) -DNDIM=$(NDIM) -DNPRE=$(NPRE) -DSOLVER$(SOLVER) -DNVAR=$(NVAR) $(PFLAGS) $(DNEC) -DNVECTOR=$(NVECTOR) #-DNOSYSTEM #-D$(HILBERT) disable NOSYSTEM for gfortran and ftn
MOD = mod

# Sources directories are searched in this exact order
VPATH = $(PATCH):../$(SOLVER):../hydro:../pm:../poisson:../amr



#############################################################################


all: ramses
	$(F90) $(FFLAGS) amr_commons.o cooling_module.o units.o hydro_commons.o hydro_parameters.o pm_commons.o pm_parameters.o add_list.o nbors_utils.o remove_list.o interpol_hydro.o physical_boundaries.o hydro_flag.o godunov_utils.o poisson_commons.o refine_utils.o poisson_parameters.o boundana.o hydro_boundary.o sort.o bisection.o hilbert.o load_balance.o virtual_boundaries.o particle_tree.o sink_particle.o update_time.o amr_parameters.o read_hydro_params.o read_params.o title.o init_amr.o init_time.o init_hydro.o init_poisson.o condinit.o init_flow_fine.o rho_ana.o rho_fine.o init_refine.o init_part.o gravana.o boundary_potential.o write_screen.o output_hydro.o output_part.o output_poisson.o output_amr.o output_rectest.o uplmde.o umuscl.o godunov_fine.o light_cone.o feedback.o synchro_hydro_fine.o interpol_phi.o phi_fine_cg.o flag_utils.o multigrid_fine_fine.o multigrid_fine_coarse.o multigrid_fine_commons.o force_fine.o random.o star_formation.o synchro_fine.o courant_fine.o newdt_fine.o move_fine.o cooling_fine.o amr_step.o adaptive_loop.o clump_finder.o clump_merger.o clfind_commons.o heapsort_index.o ramses.o -o $(EXEC)$(NDIM)d
# "cp" stands for cray-PAT

%.o:%.f90
	$(F90) $(FFLAGS) -c $^ -o $@ 


#############################################################################


ramses: read_params adaptive_loop ramses.o
	echo 'ramses'
read_params: amr_commons pm_commons poisson_parameters read_hydro_params read_params.o
	echo 'read_params'
adaptive_loop: hydro_boundary init_refine interpol_hydro refine_utils poisson_commons init_amr cooling_module amr_commons amr_step pm_commons hydro_commons particle_tree flag_utils init_part init_poisson init_hydro update_time init_time title adaptive_loop.o
	echo 'adaptive_loop'
init_time: pm_commons amr_commons amr_parameters hydro_commons cooling_module title init_time.o
	echo 'init_time'
clfind_commons: clfind_commons.o
	echo 'clfind_commons'
heapsort_index: heapsort_index.o
	echo 'heapsort_index'
init_hydro: amr_commons hydro_commons init_hydro.o
	echo 'init_hydro'
init_poisson: pm_commons amr_commons poisson_commons title init_poisson.o
	echo 'init_poisson'
init_refine: hydro_boundary init_flow_fine flag_utils pm_commons virtual_boundaries hydro_commons poisson_commons amr_commons refine_utils load_balance rho_fine interpol_hydro particle_tree init_refine.o
	echo 'init_refine'
title: title.o
	echo 'title'
flag_utils: physical_boundaries pm_commons poisson_commons virtual_boundaries amr_commons nbors_utils hydro_flag units cooling_module flag_utils.o
	echo 'flag_utils'
amr_commons: amr_parameters amr_commons.o
	echo 'amr_commons'
amr_parameters: amr_parameters.o
	echo 'amr_parameters'
pm_parameters: amr_parameters pm_parameters.o
	echo 'pm_parameters'
poisson_parameters: amr_parameters poisson_parameters.o
	echo 'poisson_parameters'
read_hydro_params: amr_commons hydro_commons cooling_module read_hydro_params.o
	echo 'read_hydro_params'
hydro_commons: amr_parameters hydro_parameters hydro_commons.o
	echo 'hydro_commons'
pm_commons: amr_parameters pm_parameters random pm_commons.o
	echo 'pm_commons'
poisson_commons: amr_commons poisson_parameters poisson_commons.o
	echo 'poisson_commons'
cooling_module: amr_parameters cooling_module.o
	echo 'cooling_module'
init_amr: amr_commons hydro_commons pm_commons poisson_commons bisection load_balance title init_amr.o
	echo 'init_amr'
bisection: amr_parameters amr_commons bisection.o
	echo 'bisection'
remove_list: amr_commons pm_commons remove_list.o
	echo 'remove_list'
add_list: amr_commons pm_commons add_list.o
	echo 'add_list'
nbors_utils: amr_commons nbors_utils.o
	echo 'nbors_utils'
godunov_utils: hydro_parameters amr_parameters godunov_utils.o
	echo 'godunov_utils'
hilbert: amr_parameters hilbert.o
	echo 'hilbert'
output_poisson: amr_commons poisson_commons title output_poisson.o
	echo 'output_poisson'
units: amr_commons hydro_commons cooling_module units.o
	echo 'units'
boundary_potential: amr_commons poisson_commons boundary_potential.o
	echo 'boundary_potential'
random: amr_commons random.o
	echo 'random'
hydro_parameters: amr_parameters hydro_parameters.o
	echo 'hydro_parameters'
condinit: amr_parameters hydro_parameters condinit.o
	echo 'condinit'
boundana: amr_parameters hydro_parameters boundana.o
	echo 'boundana'
output_part: amr_commons pm_commons title output_part.o
	echo 'output_part'
umuscl: amr_parameters hydro_parameters godunov_utils umuscl.o
	echo 'umuscl'
update_time: amr_commons hydro_commons pm_commons cooling_module output_rectest update_time.o
	echo 'update_time'
uplmde: amr_parameters hydro_parameters uplmde.o
	echo 'uplmde'
light_cone: amr_parameters amr_commons pm_commons light_cone.o
	echo 'light_cone'
init_part: amr_commons pm_commons load_balance init_part.o
	echo 'init_part'
gravana: amr_parameters amr_commons poisson_parameters poisson_commons gravana.o
	echo 'gravana'
hydro_boundary: boundana poisson_parameters amr_commons hydro_commons hydro_boundary.o
	echo 'hydro_boundary'
rho_ana: amr_parameters hydro_parameters poisson_parameters rho_ana.o
	echo 'rho_ana'
interpol_hydro: amr_commons hydro_commons poisson_commons interpol_hydro.o
	echo 'interpol_hydro'
physical_boundaries: amr_commons poisson_parameters nbors_utils physical_boundaries.o
	echo 'physical_boundaries'
courant_fine: poisson_commons hydro_commons amr_commons godunov_utils courant_fine.o
	echo 'courant_fine'
particle_tree: pm_commons nbors_utils add_list remove_list amr_commons particle_tree.o
	echo 'particle_tree'
output_hydro: amr_commons hydro_commons title output_hydro.o
	echo 'output_hydro'
output_rectest: amr_commons hydro_commons cooling_module units title output_rectest.o
	echo 'output_rectest'
cooling_fine: sink_particle units hydro_commons amr_commons cooling_module cooling_fine.o
	echo 'cooling_fine'
godunov_fine: umuscl hydro_commons nbors_utils poisson_commons interpol_hydro amr_commons godunov_fine.o
	echo 'godunov_fine'
newdt_fine: courant_fine pm_commons hydro_commons amr_commons poisson_commons newdt_fine.o
	echo 'newdt_fine'
rho_fine: rho_ana virtual_boundaries pm_commons hydro_commons nbors_utils amr_commons poisson_commons cooling_module rho_fine.o
	echo 'rho_fine'
synchro_hydro_fine: amr_commons hydro_commons poisson_commons synchro_hydro_fine.o
	echo 'synchro_hydro_fine'
refine_utils: pm_commons virtual_boundaries hydro_commons amr_commons nbors_utils poisson_commons interpol_hydro refine_utils.o
	echo 'refine_utils'
multigrid_fine_coarse: amr_commons poisson_commons pm_commons nbors_utils multigrid_fine_coarse.o
	echo 'multigrid_fine_coarse'
output_amr: cooling_module output_poisson units pm_commons amr_commons hydro_commons write_screen output_part output_hydro output_poisson output_amr.o
	echo 'output_amr'
synchro_fine: amr_commons pm_commons poisson_commons nbors_utils synchro_fine.o
	echo 'synchro_fine'
write_screen: amr_commons poisson_commons hydro_commons pm_commons sort write_screen.o
	echo 'write_screen'
hydro_flag: cooling_module pm_commons hydro_commons godunov_utils nbors_utils amr_commons poisson_commons hydro_flag.o
	echo 'hydro_flag'
interpol_phi: amr_commons poisson_commons interpol_phi.o
	echo 'interpol_phi'
init_flow_fine: hydro_boundary cooling_module interpol_hydro hydro_parameters amr_parameters amr_commons hydro_commons virtual_boundaries condinit title init_flow_fine.o
	echo 'init_flow_fine'
virtual_boundaries: bisection physical_boundaries hydro_commons amr_commons nbors_utils poisson_commons virtual_boundaries.o
	echo 'virtual_boundaries'
force_fine: virtual_boundaries amr_commons hydro_commons pm_commons poisson_commons boundary_potential interpol_phi gravana force_fine.o
	echo 'force_fine'
move_fine: amr_commons hydro_commons nbors_utils pm_commons poisson_commons move_fine.o
	echo 'move_fine'
load_balance: hydro_boundary bisection hydro_commons pm_commons particle_tree amr_commons virtual_boundaries flag_utils hilbert refine_utils load_balance.o
	echo 'load_balance'
phi_fine_cg: gravana boundary_potential poisson_commons pm_commons amr_commons hydro_commons virtual_boundaries interpol_phi phi_fine_cg.o
	echo 'phi_fine_cg'
multigrid_fine_fine: poisson_commons pm_commons nbors_utils amr_commons multigrid_fine_fine.o
	echo 'multigrid_fine_fine'
multigrid_coarse: force_fine phi_fine_cg poisson_commons pm_commons hydro_commons nbors_utils amr_commons virtual_boundaries multigrid_coarse.o
	echo 'multigrid_coarse'
star_formation: random cooling_module units pm_commons hydro_commons amr_commons remove_list add_list star_formation.o
	echo 'star formation'
feedback: add_list remove_list virtual_boundaries amr_commons hydro_commons nbors_utils units interpol_hydro cooling_module pm_commons feedback.o
	echo 'feedback'
sink_particle: hydro_boundary pm_commons add_list remove_list hydro_commons particle_tree nbors_utils units amr_commons virtual_boundaries interpol_hydro cooling_module sort sink_particle.o
	echo 'sink_particle'
sort: amr_parameters sort.o
	echo 'sort'
clump_finder: amr_commons pm_commons hydro_commons clfind_commons cooling_module random particle_tree output_part clump_merger units remove_list add_list clump_finder.o
	echo 'clump_finder'
clump_merger: amr_commons hydro_commons pm_commons clfind_commons poisson_commons clump_finder units heapsort_index clump_merger.o
	echo 'clump_merger'

multigrid_fine_commons: phi_fine_cg poisson_parameters boundary_potential multigrid_fine_fine pm_commons poisson_commons nbors_utils amr_commons multigrid_coarse virtual_boundaries multigrid_fine_coarse interpol_phi multigrid_fine_commons.o
	echo 'multigrid_fine_commons'
amr_step: sink_particle move_fine feedback update_time uplmde hydro_commons synchro_hydro_fine godunov_fine rho_fine particle_tree output_amr cooling_fine light_cone amr_commons newdt_fine synchro_fine virtual_boundaries flag_utils star_formation multigrid_fine_commons force_fine phi_fine_cg boundary_potential interpol_hydro refine_utils hydro_boundary poisson_commons load_balance pm_commons clump_finder amr_step.o
	echo 'amr_step'





#############################################################################



clean :
	rm -f *.o *.i *.$(MOD) *$(MOD).f90 *~ ../*/*~ ../*/*/*~


#############################################################################
