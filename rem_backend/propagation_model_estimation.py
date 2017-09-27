#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import date, datetime, timedelta
import math
import mysql.connector
import rem_backend.insert_query as insert_query
from numpy import matrix
from numpy import linalg
import numpy
import os

__author__ = "Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{valentin}@feit.ukim.edu.mk"

'''
Propagation model estimation Module 
Calculates propagation model for the REM backend
'''


def get_distance(dev1_mac, dev2_mac):
	'''
	Calculates distance between to devices
	Args:
		dev1_mac: mac addres of the first device
		dev2_mac: mac addres of the second device
		
	Returns:
		distance: the distance between the devices in meters
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()
	R = 6378*1000

	distance = -1

	query1 = ("select x_coord, y_coord, global_loc_id, floor from devices where mac_address = '"+str(dev1_mac)+"';")

	query2 = ("select x_coord, y_coord, global_loc_id, floor from devices where mac_address = '"+str(dev2_mac)+"';")

	cursor.execute(query1)
	row1 = cursor.fetchone()

	#check if there is data if not find from estimated locs
	if row1 is None:
		query1 = ("select x_coord, y_coord, global_loc_id, floor from estimated_locations where tx_mac_address = '"+str(dev1_mac)+"';")
		cursor.execute(query1)
		row1 = cursor.fetchone()

	cursor.execute(query2)
	row2 = cursor.fetchone()

	#check if there is data if not find from estimated locs
	if row2 is None:
		query2 = ("select x_coord, y_coord, global_loc_id, floor from estimated_locations where tx_mac_address = '"+str(dev2_mac)+"';")
		cursor.execute(query2)
		row2 = cursor.fetchone()

	dev1 = row1
	dev2 = row2
	if dev1 is not None and dev2 is not None:
		h = abs(dev1[3] - dev2[3])*4
	else:
		return None

	# check if global loc is the same, if so calc the distance only on the x,y,z coord. if not calc distance based on long/lat

	if dev1[2] == dev2[2]:
		distance = math.sqrt(math.pow(dev1[0]-dev2[0],2)+math.pow(dev1[1]-dev2[1],2)+math.pow(h,2))

	else:

		query = ("select x_coord, y_coord from global_location where id ="+str(dev1[2])+" or id ="+str(dev2[2])+";")
		cursor.execute(query)
		coords = cursor.fetchall()

		coord1 = coords[0]
		coord2 = coords[1]
		lat1 = coord1[1]
		long1  = coord1[0]
		lat2 = coord2[1]
		long2  = coord2[0]

		# calc global lat/long for devices
		lat1n = lat1 + (dev1[1]/R)*(180/math.pi)
		long1n = long1 + (dev1[0]/R)*(180/math.pi)/math.cos(lat1*math.pi/180)
		lat2n = lat2 + (dev2[1]/R)*(180/math.pi)
		long2n = long2 + (dev2[0]/R)*(180/math.pi)/math.cos(lat2*math.pi/180)

		#calculate long/lat distance 
		latRad1 = math.radians(lat1n)
		longRad1 = math.radians(long1n)

		latRad2 = math.radians(lat2n)
		longRad2 = math.radians(long2n)

		dlon = longRad1 - longRad2
		dlat = latRad1 - latRad2

		a = math.sin(dlat/2)**2 + math.cos(latRad1)*math.cos(latRad2)*math.sin(dlon/2)**2
		c = 2*math.atan2(math.sqrt(a),math.sqrt(1-a))

		d = R*c
		distance = math.sqrt(math.pow(d,2) + math.pow(h,2))



	cursor.close()
	cnx.close()


	return distance; 

def get_PL_link(dev1_mac, dev2_mac, timespan, chann):
	'''
	Calculates the path loss on the link between two devices
	Args:
		dev1_mac: mac addres of the first device
		dev2_mac: mac addres of the second device
		timespan: the timespan of interest
		chann: the channel of interest
		
	Returns:
		PL: the pathloss value in dB
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select avg(value-20) from rssi_meas where active_channel = "+str(chann)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"' and ((tx_mac_address = '"+str(dev1_mac)+"' and rx_mac_address ='"+str(dev2_mac)+"') or (tx_mac_address = '"+str(dev2_mac)+"' and rx_mac_address = '"+str(dev1_mac)+"'));")

	print(query)
	cursor.execute(query)

	PL = cursor.fetchone();

	if PL is None:
		PL = null;


	cursor.close()
	cnx.close()


	return PL; 

def get_PL_chann_dev(timespan, chann):
	'''
	get pathloss between all active pair of devices on a given channel
	Args:
		timespan: the timespan of interest
		chann: the channel of interest
		
	Returns:
		PL: the pathloss value in dB
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select least(tx_mac_address, rx_mac_address) as l1, greatest(tx_mac_address, rx_mac_address) as l2, avg(value) as avg_val from rssi_meas f where active_channel = "+str(chann)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"' group by least(tx_mac_address, rx_mac_address), greatest(tx_mac_address, rx_mac_address);")

	cursor.execute(query)

	PL = cursor.fetchall();

	if PL is None:
		PL = null;


	cursor.close()
	cnx.close()


	return PL; 


def get_PL_chann(timespan, chann):
	'''
	get pathloss on a given channel
	Args:
		timespan: the timespan of interest
		chann: the channel of interest
		
	Returns:
		PL: the pathloss value in dB
	'''

	PL_data = get_PL_chann_dev(timespan, chann)
	print(PL_data)

	PL = []
	for row in PL_data:
		dist = get_distance(row[0], row[1])
		if dist is not None: PL.append([dist, abs(row[2])]) #dev1_add, dev2_add, loss

	#PL.append([70,90])	# for testing purposes
	return PL; 


def get_PL_chann_link(timespan, chann, tx, rx):
	'''
	get the path loss on a given link between two devices
	Args:
		timespan: the timespan of interest
		chann: the channel of interest
		tx: tx of interest
		rx: rx of interest
		
	Returns:
		data: dictionary of the path loss L0, exp, sigma 
	'''

	ch_mod = get_chann_model(timespan, chann)
	d = get_distance(tx,rx)
	PL = -(ch_mod['L0'] + 10*ch_mod['alpha']*math.log10(d) + ch_mod['sigma'])

	return PL; 


def get_chann_model(timespan, chann):
	'''
	get the model L0, exp, sigma on a given channel (reference distance d0 = 1m)
	Args:
		timespan: the timespan of interest
		chann: the channel of interest
		
	Returns:
		data: dictionary of the path loss L0, exp, sigma 
	'''

	hth = numpy.zeros(shape=(2,2))
	HtH = numpy.asmatrix(hth)
	HtP = numpy.zeros(2)
	C = numpy.zeros(2)
	PL = get_PL_chann(timespan, chann)
	data = None
	
	if len(PL) > 0:
		h = numpy.zeros(shape=(len(PL),2))
		H = numpy.asmatrix(h)
		Ptx = 20 # dBms max Tx power of WiFI

		j = 0
		for row in PL:
			print(row)
			H[j,0] = 1
			H[j,1] = -10*math.log10(row[0])
			HtH[0,0] += math.pow(H[j,0],2)
			HtH[0,1] += H[j,0]*H[j,1]
			HtH[1,0] += H[j,1]*H[j,0]
			HtH[1,1] += math.pow(H[j,1],2)
			HtP[0] += H[j,0]*row[1]
			HtP[1] += H[j,1]*row[1]
			j += 1

		HtHinv = HtH.I

		C[0] = HtHinv[0,0]*HtP[0] + HtHinv[0,1]*HtP[1]
		C[1] = HtHinv[1,0]*HtP[0] + HtHinv[1,1]*HtP[1]

		j = 0
		sigma = 0
		for row in PL:
			sigma += math.pow(H[j,0]*C[0]+H[j,1]*C[1]-row[1],2)
			j += 1


		sigma /= len(PL)
		L0 = Ptx - C[0]
		alpha = abs(C[1])
		#maxDist = max(b for (a,b) in PL)
	
		data = (str(L0), str(alpha), str(sigma), 1, datetime.now(), chann) 
		insert_query.insert_propagation_model(data)

		data = dict()
		data['L0'] = L0
		data['alpha'] = alpha
		data['sigma'] = sigma

	return data; 




