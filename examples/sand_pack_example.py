import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import pyperc

plt.close('all')

# Invading and defending fluid density
invading_fluid_density = 2 # kg/m3, C02
defending_fluid_density = 996 # kg/m3, Water
# Contact angles, one per grain type
contact_angles = [150,150,150] # degress, for the invading fluid on each grain
# Surface tension
surface_tension = 72*0.001 # N/m
# Iterations
max_iterations = -1 # Run to completion
# Growth model
p = 0.0
seed = 340995

# Get an IP model instance
ip = pyperc.model.InvasionPercolation()
 
# Setup regular grid
Nx = 240
Ny = 1
Nz = 511
cell_size = 0.001087 # m
radius = np.loadtxt('data/Sandpack_radius_cm.txt')/100 # sorted by z, then y, then x, convert cm to m
grain = np.loadtxt('data/Sandpack_type.txt') # sorted by z, then y, then x

ip.setup_grid(Nx,Ny,Nz,cell_size, radius, grain)
ip.pores['grain'] = ip.pores['grain'] - 1 # zero based index

radius = ip.pores.radius.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(radius[:,0,:], origin='lower')
plt.colorbar()
plt.title('Radius (m)')
plt.tight_layout()

grain = ip.pores.grain.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(grain[:,0,:], origin='lower')
plt.title('Grain type')
plt.tight_layout()

# Initialize pores
ip.initialize_pores(contact_angles, invading_fluid_density, 
                    defending_fluid_density, surface_tension)

# Reset start location and update neighbors
# Circle centered at (116.5, 29.5) with radius 5.5
# (x-116.5)^2 + (z-29.5)^2 < 5.5^2
ip.pores.start = 0
ip.pores.loc[pow(ip.pores.x-116.5*cell_size,2) + pow(ip.pores.z-29.5*cell_size,2) < pow(5.5*cell_size,2),'start'] = 1
ip.pores.occupy = ip.pores.start
ip.update_neighbors()

start = ip.pores.start.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(start[:,0,:], origin='lower')
plt.colorbar()
plt.title('Start')

pc = ip.pores.pc.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(pc[:,0,:], origin='lower')
plt.colorbar()
plt.title('Capillary pressure (Pa)')

pg = ip.pores.pg.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(pg[:,0,:], origin='lower')
plt.colorbar()
plt.title('Gravity/buoyancy pressure (Pa)')

pt = ip.pores.pt.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(pt[:,0,:], origin='lower')
plt.colorbar()
plt.title('Total pressure (Pa)')

plt.figure()
plt.scatter(ip.pores['radius'], ip.pores['pt'])
plt.xlabel('Radius (m)')
plt.ylabel('Total pressure (Pa)')

# Run invasion percolation
ip.run(max_iterations,p,seed)

# Plot results
plt.figure()
plt.plot(ip.results.threshold)
plt.xlabel('Iteration')
plt.ylabel('Filled pressure (Pa)')

N_all = len(ip.pores.radius)
x_all = np.sort(ip.pores.radius)
f_all = np.array(range(N_all))/float(N_all)
filled_radius = ip.pores.radius.loc[ip.pores.occupy == 1]
N_filled = len(filled_radius)                               
x_filled = np.sort(filled_radius)
f_filled = np.array(range(N_filled))/float(N_filled)
plt.figure()
plt.plot(x_all, f_all, label='All radii')
plt.plot(x_filled, f_filled, label='Filled radii')
plt.xlabel('Radius (m)')
plt.ylabel('Empirical CDF')
plt.legend()

occupy = ip.pores.occupy.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(occupy[:,0,:], origin='lower')
plt.title('Occupied pores')

iteration = pd.Series(index=ip.pores.index, data=np.nan) #-ip.results.index.max().max()*0.05) 
iteration1 = pd.Series(index = ip.results.node, data = ip.results.index)
iteration[iteration1.index] = iteration1
iteration = iteration.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(iteration[:,0,:], origin='lower', cmap='nipy_spectral') 
plt.colorbar()
plt.title('Occupied pores, iteration')

threshold = pd.Series(index=ip.pores.index, data=np.nan) 
threshold1 = pd.Series(index = ip.results.node, data = ip.results.threshold.values)
threshold[threshold1.index] = threshold1
threshold = threshold.values.reshape((Nz,Ny,Nx))
plt.figure()
plt.imshow(threshold[:,0,:], origin='lower', cmap='nipy_spectral') 
plt.colorbar()
plt.title('Occupied pores, threshold')
