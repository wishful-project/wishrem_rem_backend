import math
import numpy as np


__author__ = "Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{valentin}@feit.ukim.edu.mk"


'''
Localization Module 
Used for processing of the localization process in the REM backend
'''

def ML_grid(xs, ys, zs, rss, ulx=0, uly=15, drx=32, dry=0, nx=50, ny=50, nz=50):
	'''
	Localization process based on ML algorithm
	Args:
		xs,ys, zs: vectors of coordinates for the x, y, z axis
		rss: vector of measured values on coordinates xs, ys, zs
		ulx, uly, drx, dry: upper left and lower right corner coordinates of the area of interest for the loc process
		nx,ny, nz: resolution for x,y,z axis
		in_type: interpolation algorithm 
	Returns:
		results (tuple consisted of estimated x,y,z coordinates and respective estimated tx power)
	'''

	

	X = np.array(xs)
	#print(X)
	Y = np.array(ys)
	#print(Y)
	Z = np.array(zs)
	#print(Z)
	P = np.array(rss)
	#print(P)

	noMeasP = len(xs)
	xmin = ulx
	ymin = dry
	xmax = drx
	ymax = uly
	zmin = np.amin(zs)
	zmax = np.amax(zs)
	#print(zmin)
	xres = abs((drx-ulx)/nx)
	yres = abs((dry-uly)/ny)
	zres = abs((zmax-zmin)/nz)

	xE = -1
	yE = -1
	zE = -1
	pE = -1

	xsize = nx
	ysize = ny
	zsize = nz

	hp = np.zeros(shape=((xsize+1)*(ysize+1)*(zsize+1),3))
	points = np.asmatrix(hp)
	#print(points)
	
	ii = 0
	for i in range(0, xsize+1):
		for j in range(0, ysize+1):
			for k in range(0, zsize+1):
				points[ii,0] = i*xres+xmin
				points[ii,1] = j*yres+ymin
				points[ii,2] = k*zres+zmin
				
				for ik in range(0,noMeasP):
					if((X[ik]==points[ii,0]) and (Y[ik]==points[ii,1]) and (Z[ik]==points[ii,2])):
						X[ik] += 0.00001
						Y[ik] += 0.00001
						Z[ik] += 0.00001
				ii+=1

	
	L = -math.inf
	D = np.zeros(noMeasP)
	D2 = np.zeros(noMeasP)
	DP2 = np.zeros(noMeasP)
	Pp = np.zeros(noMeasP)
	Dnp = np.zeros(noMeasP)
	Pm = np.zeros(noMeasP)
	
	for i in range(0, (xsize+1)*(ysize+1)*(zsize+1)):
		Lnp = 0
		sumD = 0
		sumD2 = 0
		sumP = 0
		sumDP2 = 0
		for j in range(0,noMeasP):
			D[j] = 10*math.log10(math.sqrt(math.pow(X[j]-points[i,0],2)+math.pow(Y[j]-points[i,1],2)+math.pow(Z[j]-points[i,2],2)))
			D2[j] = math.pow(D[j],2)
			DP2[j] = D[j]*P[j]
			sumD +=D[j]
			sumD2 +=D2[j]
			sumP +=P[j]
			sumDP2 += DP2[j]

		Da = sumD/noMeasP
		Da2 = math.pow(Da,2)
		D2a = sumD2/noMeasP
		Pa = sumP/noMeasP
		DPa = sumDP2/noMeasP
		P0 = (D2a*Pa-Da*DPa)/(D2a-Da2)
		npp = (Da*Pa-DPa)/(D2a-Da2)

		for j in range(0,noMeasP):
			Pm[j] = P[j] - P0 + npp * D[j]
			Lnp += math.pow(Pm[j],2)

		Ln = -Lnp/2
		if (Ln > L):
			L = Ln
			xE = points[i,0]
			yE = points[i,1]
			zE = points[i,2]
			pE = 10*math.log10(abs(P0))
		
	
	results = []
	results.append(xE)
	results.append(yE)
	results.append(zE)
	results.append(pE)
	
	return results

