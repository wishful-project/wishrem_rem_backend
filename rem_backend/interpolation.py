import numpy as np
#import matplotlib.pyplot as plt
from scipy.interpolate import Rbf

__author__ = "Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{valentin}@feit.ukim.edu.mk"

'''
Interpolation Module 
Calculates spatial interpolation for the REM backend. Used for duty cycle purposes. 
'''


def interpolation(xs,ys,zs,xmin,ymin,xmax,ymax,nx=50,ny=50,in_type=1):
	'''
	Main interfacing function for the interpolation. 
	Args:
		xs,ys: vectors of coordinates for the x, y, axis
		zs: vector of measured values on coordinates xs, ys
		xmin,ymin,xmax,ymax: range of min and max values for coordinates
		nx,ny: resolution for x,y axis
		in_type: interpolation algorithm 
	Returns:
		res (tuple consisted of x,y coordinates and respective interpolated value)
	'''
	# Setup of the interpolation data sets
	#n = len(x)
	#x, y, z = map(np.random.random, [n, n, n])
	x = np.array(xs)
	y = np.array(ys)
	z = np.array(zs)
	xi = np.linspace(xmin, xmax, nx)
	yi = np.linspace(ymin, ymax, ny)
	xi, yi = np.meshgrid(xi, yi)
	xi, yi = xi.flatten(), yi.flatten()
	hm = 0

	if (in_type == 1): 
    # Calculate IDW
		grid1 = idw(x,y,z,xi,yi)
		hm = grid1
		# Debuging...
		# grid1 = grid1.reshape((ny, nx))
		#plot(x,y,z,grid1)
		#plt.title(' IDW')
	elif (in_type == 2):
    # Calculate scipy's RBF
		grid2 = rbf(x,y,z,xi,yi)
		hm = grid2
		# Debuging...
		# grid2 = grid2.reshape((ny, nx))
		#plot(x,y,z,grid2)
		#plt.title("Scipy's Rbf")

	# Debuging...
	#plt.show()
	res = []
	# bounding the interpolation values to physycal representation of the duty cycle
	hm[hm>100] = 100
	hm[hm<0] = 0
	
	cnt = 0
	for elem in np.nditer(hm):
		res.append([xi[cnt],yi[cnt],hm[cnt]])
		cnt += 1

	
	return res

def idw(x, y, z, xi, yi):
	'''
	Iverse weighteddistance based interpolation algorithm
	Args:
		x,y: vectors of coordinates for the x, y axis
		z: vector of dutycycle values
		xi, yi: grid of location points used for interpolation
	Returns:
		zi (vector of calculated/interpolated values)
	'''
	dist = distance_matrix(x,y, xi,yi)

    # In IDW, weights are 1 / distance --> this can change based on some propagation model preferences and information
	weights = 1.0 / dist

    # Make weights sum to one
	weights /= weights.sum(axis=0)

    # Multiply the weights for each interpolated point by all observed Z-values
	zi = np.dot(weights.T, z)
	return zi

def rbf(x, y, z, xi, yi):
	'''
	Radial basis function based interpolation algorithm
	Args:
		x,y: vectors of coordinates for the x, y axis
		z: vector of dutycycle values
		xi, yi: grid of location points used for interpolation
	Returns:
		zi (vector of calculated/interpolated values)
	'''
	interp = Rbf(x, y, z, function='linear')
	return interp(xi, yi)

def distance_matrix(x0, y0, x1, y1):
    	obs = np.vstack((x0, y0)).T
    	interp = np.vstack((x1, y1)).T

    	d0 = np.subtract.outer(obs[:,0], interp[:,0])
    	d1 = np.subtract.outer(obs[:,1], interp[:,1])

    	return np.hypot(d0, d1)

#def plot(x,y,z,grid):
#    plt.figure()
#    plt.imshow(grid, extent=(x.min(), x.max(), y.max(), y.min()))
#    plt.hold(True)
#    plt.scatter(x,y,c=z)
#    plt.colorbar()

