#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import os
import rem_backend.interpolation as interpolation
import rem_backend.localization as localization
import math

__author__ = "Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{valentin}@feit.ukim.edu.mk"

'''
query data Module 
Main REM interfacing function. Should be used by any RRM that connects to the platform
'''

def get_device(mac_add):
	'''
	Returs information for a specific device 
	Args:
		mac_add: Mac address of the device
	Returns:
		device: Dictionary of device information. (channel capabilities, location, mode of operation, stauts, channel)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	query = ("select chan_capab, x_coord, y_coord, global_loc_id, floor, mode, status, active_channel, active_channel_sup from devices where mac_address  = '"+mac_add+"';")

	cursor.execute(query)
	device = dict();
	rows = cursor.fetchone()

	if rows is None:
		device = None
	else:
		device['chan_capab'] = rows[0]
		device['x_coord'] = rows[1]
		device['y_coord'] = rows[2]
		device['global_location'] = rows[3]
		device['floor'] = rows[4]
		device['mode'] = rows[5]
		device['status'] = rows[6]
		device['channel'] = rows[7]
		device['channel_sup'] = rows[8]

	cursor.close()
	cnx.close()


	return device; 


def get_pathloss_model(channel):
	'''
	Returs the path loss model for a specific channel 
	Args:
		channel: the channel of interest
	Returns:
		device: Dictionary of channel_model. (L0, alpha, sigma, d0)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	query = ("select L0, alpha, sigma, d0 from propagation_model where channel = " +str(channel)+ " order by timestamp DESC limit 1")

	cursor.execute(query)
	channel_model = dict();
	rows = cursor.fetchone()

	if rows is None:
		channel_model['L0'] = 'none'

	else:
		channel_model['L0'] = rows[0]
		channel_model['alpha'] = rows[1]
		channel_model['sigma'] = rows[2]
		channel_model['d0'] = rows[3] 

	cursor.close()
	cnx.close()


	return channel_model; 


def get_channel_model(links, channel, timespan):
	'''
	Returs the channel model for a specific number of links
	Comment:  Obsolete for now. maybe can be used for the future, if per device filtering is required
	
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select if (sum_cnt>"+str(links)+", sum_cnt, 0) from (select sum(cnt) as sum_cnt from (select tx_mac_address, count(distinct rx_mac_address) as cnt from (select * from propagation_model where channel = "+str(channel)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmptb group by tx_mac_address) temtab) sumtab;")

	cursor.execute(query)

	sum_cnt = cursor.fetchone();

	channel_model = dict();

	if sum_cnt[0] > 0:
		query = ("select avg(L0), avg(alpha) from propagation_model;")
		cursor.execute(query)

		rows = cursor.fetchone()

		if rows is None:
			channel_model['L0'] = 'none'

		else:
			channel_model['L0'] = rows[0]
			channel_model['alpha'] = rows[1]
	else:
		print("nema uslovi")
		channel_model['L0'] = 'none'

	cursor.close()
	cnx.close()


	return channel_model; 




def get_tx_locations(channel, floor, timespan):
	'''
	Returs the tx locations for a specific channel floor and timespan
	Args:
		channel: the channel of interest
		floor: the floor of interest
		timepsan: the timespan of interest
	Returns:
		tx_loc: List of location tupples. (mac address, x and y coordinates, global location id, tx power)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select tx_mac_address, x_coord, y_coord, global_loc_id, tx_power from estimated_locations where floor = "+str(floor)+" and channel = "+str(channel)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"';")

	cursor.execute(query)
	tx_loc = cursor.fetchall()

	cursor.close()
	cnx.close()


	return tx_loc; 


def get_channel_status(channel, threshold, timespan):
	'''
	Returs the channel status for a specific channel and timespan. Efectively cooperative spectrum sensing based on hard decision combining
	Args:
		channel: the channel of interest
		threshold: duty cycle threshold
		timepsan: the timespan of interest
	Returns:
		status: channel status (0--> free, 1--> ocupied)
	'''
	

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select if(avg_val>"+str(threshold)+",1,0) from (select avg(value) as avg_val from duty_cycle where channel = "+str(channel)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmpdb;")

	cursor.execute(query)
	status = cursor.fetchone()

	cursor.close()
	cnx.close()


	return status; 

def get_channel_status_by_area(channel, threshold, timespan, ulx=0, uly=1000, drx=1000, dry=0):
	'''
	Returs the channel status for a specific channel, area and timespan. Efectively cooperative spectrum sensing based on hard decision combining
	Args:
		channel: the channel of interest
		threshold: duty cycle threshold
		timepsan: the timespan of interest
		ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
	Returns:
		status: channel status (0--> free, 1--> ocupied)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select if(avg_val>"+str(threshold)+",1,0) from (select avg(value) as avg_val from duty_cycle, (select mac_address as addr from (select mac_address, ST_GeomFromText(CONCAT('Point(',x_coord,' ', y_coord,')')) as point from devices) tmpdb where MBRContains(ST_GeomFromText('Polygon(("+str(ulx)+" "+str(dry)+","+str(ulx)+" "+str(uly)+","+str(drx)+" "+str(uly)+","+str(drx)+" "+str(dry)+","+str(ulx)+" "+str(dry)+"))'),point)) tmp where channel = "+str(channel)+" and rx_mac_address = addr and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmpavg;")

	cursor.execute(query)
	status = cursor.fetchone()

	cursor.close()
	cnx.close()


	return status; 

def get_channel_status_by_device(channel, rx_add, threshold, timespan):
	'''
	Returs the channel status for a specific channel, device and timespan. 
	Args:
		channel: the channel of interest
		rx_add: mac addres of the device
		threshold: duty cycle threshold
		timepsan: the timespan of interest
	Returns:
		status: channel status (0--> free, 1--> ocupied)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select if(avg_val>"+str(threshold)+",1,0) from (select avg(value) as avg_val from duty_cycle where rx_mac_address = '"+rx_add+"' and channel = "+str(channel)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmpdb;")

	cursor.execute(query)
	status = cursor.fetchone()

	cursor.close()
	cnx.close()


	return status; 


def get_channel_status_all_by_device(rx_add, threshold, timespan):

	'''
	Returs the list of channel status for all channels, specific device and timespan.
	Args:
		rx_add: the channel of interest
		threshold: duty cycle threshold
		timepsan: the timespan of interest
	Returns:
		dc: list of tuple (channel, channel status) (0--> free, 1--> ocupied)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select channel, if(avg_val>"+str(threshold)+",1,0) from (select channel, avg(value) as avg_val from (select * from duty_cycle where rx_mac_address = '"+str(rx_add)+"' and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmpdb group by channel) tempdb;")

	cursor.execute(query)
	dc = cursor.fetchall()

	cursor.close()
	cnx.close()


	return dc; 

def get_channel_status_all(threshold, timespan):

	'''
	Returs the list of channel status for all channels, and timespan. Efectively cooperative spectrum sensing based on hard decision combining 
	Args:
		threshold: duty cycle threshold
		timepsan: the timespan of interest
	Returns:
		dc: list of tuple (channel, channel status) (0--> free, 1--> ocupied)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select channel, if(avg_val>"+str(threshold)+",1,0) from (select channel, avg(value) as avg_val from (select * from duty_cycle where timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmpdb group by channel) tempdb;")

	cursor.execute(query)
	dc = cursor.fetchall()

	cursor.close()
	cnx.close()


	return dc; 

def get_duty_cycle(channel, timespan):
	'''
	Returs the duty cycle for a channel and timespan of interest
	Args:
		channel: channel of interest
		timepsan: the timespan of interest
	Returns:
		dc: the duty cycle value
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select avg(value) from duty_cycle where channel = "+str(channel)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"';")

	cursor.execute(query)
	dc = cursor.fetchone()

	cursor.close()
	cnx.close()


	return dc; 

def get_duty_cycle_by_area(channel, timespan, ulx=0, uly=1000, drx=1000, dry=0):
	'''
	Returs the duty cycle for a channel, area and timespan of interest
	Args:
		channel: channel of interest
		timepsan: the timespan of interest
		ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
	Returns:
		dc: the duty cycle value
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select avg(value) as avg_val from duty_cycle, (select mac_address as addr from (select mac_address, ST_GeomFromText(CONCAT('Point(',x_coord,' ', y_coord,')')) as point from devices) tmpdb where MBRContains(ST_GeomFromText('Polygon(("+str(ulx)+" "+str(dry)+","+str(ulx)+" "+str(uly)+","+str(drx)+" "+str(uly)+","+str(drx)+" "+str(dry)+","+str(ulx)+" "+str(dry)+"))'),point)) tmp where channel = "+str(channel)+" and rx_mac_address = addr and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"';")

	
	cursor.execute(query)
	dc = cursor.fetchall()

	cursor.close()
	cnx.close()


	return dc; 


def get_duty_cycle_by_device(channel, rx_add, timespan):

	'''
	Returs the duty cycle for a channel, device and timespan of interest
	Args:
		channel: channel of interest
		rx_add: the mac address of the device
		timepsan: the timespan of interest
	Returns:
		dc: the duty cycle value
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select value from duty_cycle where rx_mac_address = '"+rx_add+"' and channel = "+str(channel)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"';")

	cursor.execute(query)
	dc = cursor.fetchall()

	cursor.close()
	cnx.close()


	return dc; 


def get_duty_cycle_all_channels_by_device(rx_add, timespan):
	'''
	Returs the duty cycle for all channels, for a given device and timespan of interest
	Args:
		rx_add: the mac address of the device
		timepsan: the timespan of interest
	Returns:
		dc: list of tupple (channel,duty cycle)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select channel, avg(value) from (select * from duty_cycle where rx_mac_address = '"+str(rx_add)+"' and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmpdb group by channel;")

	cursor.execute(query)
	dc = cursor.fetchall()

	cursor.close()
	cnx.close()


	return dc; 


def get_duty_cycle_all_channels(timespan):
	'''
	Returs the duty cycle for all channels, and timespan of interest
	Args:
		timepsan: the timespan of interest
	Returns:
		dc: list of tupple (channel,duty cycle)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select channel, avg(value) from (select * from duty_cycle where timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmpdb group by channel;")

	cursor.execute(query)
	dc = cursor.fetchall()

	cursor.close()
	cnx.close()


	return dc; 

def get_duty_cycle_heat_map(channel, timespan, nx=50, ny=50, ulx=0, uly=1000, drx=1000, dry=0, intp=1):
	'''
	Returs the duty cycle heatmap for a specific channel, area and timespan of interest
	Args:
		channel: the channel of interest
		timepsan: the timespan of interest
		ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
		nx,ny: grid resolution of heat map
		intp: interpolation type. Please check interpoaltion module for more information
	Returns:
		val: vector of calculated/interpolated values
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select max(x_coord) as x, max(y_coord) as y, avg(value) as avg_val from duty_cycle, (select x_coord, y_coord, mac_address as addr from (select x_coord, y_coord, mac_address, ST_GeomFromText(CONCAT('Point(',x_coord,' ', y_coord,')')) as point from devices) tmpdb where MBRContains(ST_GeomFromText('Polygon(("+str(ulx)+" "+str(dry)+","+str(ulx)+" "+str(uly)+","+str(drx)+" "+str(uly)+","+str(drx)+" "+str(dry)+","+str(ulx)+" "+str(dry)+"))'),point)) tmp where channel = "+str(channel)+" and rx_mac_address = addr and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"' group by rx_mac_address;")

	
	cursor.execute(query)
	dc = cursor.fetchall()
	x = []
	y = []
	val = []


	for row in dc:
		x.append(row[0])
		y.append(row[1])
		val.append(row[2])
	
	val = interpolation(x,y,val,ulx,dry,drx,uly,nx,ny,intp)
	

	cursor.close()
	cnx.close()


	return val;

def estimate_tx_location(addr, timespan=60, ulx=0, uly=15, drx=32, dry=0, nx=50, ny=50, nz=50):
	'''
	Returs the estimated location of a tx of interest
	Args:
		addr: the mac address of the localized device
		timepsan: the timespan of interest
		ulx, uly, drx, dry: upper left and lower right corner coordinates, of the area of interest
		nx,ny,nz: grid resolution of the localization algorithm
	Returns:
		val: tuple consisted of estimated x,y,z coordinates and respective estimated tx power (x,y,z,txpow)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select x_coord, y_coord, z_coord, value from devices,(select value, rx_mac_address as addr from rssi_meas where tx_mac_address = '"+str(addr)+"' and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmp where mac_address = addr;")

	
	cursor.execute(query)
	dc = cursor.fetchall()
	x = []
	y = []
	z = []
	val = []


	for row in dc:
		x.append(row[0])
		y.append(row[1])
		z.append(row[2])
		val.append(row[3])
	
	val = localization.ML_grid(x,y,z,val,ulx,dry,drx,uly,nx,ny,nz)
	

	cursor.close()
	cnx.close()


	return val; 

def estimate_tx_range(addr, timespan=60):
	'''
	Returs the estimated tx range of a tx of interest
	Args:
		addr: the mac address of the localized device
		timepsan: the timespan of interest
	Returns:
		val: dictionary with 2 points in 3D space (xmin,ymin,zmin,xmax,ymax,zmax)
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select x_coord, y_coord, z_coord, value from devices,(select value, rx_mac_address as addr from rssi_meas where tx_mac_address = '"+str(addr)+"' and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"') tmp where mac_address = addr;")

	cursor.execute(query)
	dc = cursor.fetchall()
	x = []
	y = []
	z = []

	for row in dc:
		x.append(row[0])
		y.append(row[1])
		z.append(row[2])

	val = None

	if len(x) > 0:
		val = {}
		val['xmin'] = min(x)
		val['xmax'] = max(x)
		val['ymin'] = min(y)
		val['ymax'] = max(y)
		val['zmin'] = min(z)
		val['zmax'] = max(z)

	cursor.close()
	cnx.close()

	return val; 


#get list of occupied channels from DB
def get_occupied_channels():

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	query = ("select active_channel from devices where status = 2 group by active_channel;")

	
	cursor.execute(query)
	dc = cursor.fetchall()
	
	cursor.close()
	cnx.close()


	return dc;

#get list of occupied channels from DB
def get_occupied_channels_count():

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	query = ("select count(active_channel), active_channel from devices where status = 2 group by active_channel;")

	
	cursor.execute(query)
	dc = cursor.fetchall()
	
	cursor.close()
	cnx.close()


	return dc;

def get_ap_statistics(timespan=1):
	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select ap_mac_address, avg(total_tx_retries) as avg_tx_retries, avg(total_tx_failed) as avg_tx_failed, avg(total_tx_throughput) as avg_tx_throughput, avg(total_rx_throughput) as avg_rx_throughput, avg(total_tx_activity) as avg_tx_activity, avg(total_rx_activity) as avg_rx_activity from ap_statistics where timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"' group by ap_mac_address;")

	cursor.execute(query)
	apstats = cursor.fetchall()

	cursor.close()
	cnx.close()

	return apstats;

def get_ap_degraded_retries(timespan=1, retries_threshold=10):
	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select ap_mac_address, avg_tx_retries from (select ap_mac_address, avg(total_tx_retries) as avg_tx_retries from ap_statistics where timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"' group by ap_mac_address) tmp where avg_tx_retries >= "+str(retries_threshold)+";")

	cursor.execute(query)
	apdeg = cursor.fetchall()

	cursor.close()
	cnx.close()

	return apdeg;

#get all active devices form DB on a given channel and timespan
def get_all_active_devices_on_channel(chann, timespan=10):

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()
	stopdate = datetime.now()
	startdate = stopdate-timedelta(minutes=timespan)

	query = ("select tx_mac_address from rssi_meas where active_channel = "+str(chann)+" and timestamp between '"+str(startdate)+"' and '"+str(stopdate)+"' group by tx_mac_address;")

	cursor.execute(query)
	rows = cursor.fetchall()

	cursor.close()
	cnx.close()

	return rows; 
