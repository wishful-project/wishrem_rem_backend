#!/usr/bin/python3
# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import date, datetime, timedelta
import mysql.connector
import os

__author__ = "Valentin Rakovic"
__copyright__ = "Copyright (c) 2017, Faculty of Electrical Engineering and Information Technologies, UKIM, Skopje, Macedonia"
__version__ = "0.1.0"
__email__ = "{valentin}@feit.ukim.edu.mk"

'''
Insert query Module 
Iserts data to the REM database
'''

def insert_device_location(data_device):
	'''
	Inserts device location in the database
	Args:
		data_device: the data used for inserting
	'''
	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root', password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_device = ("REPLACE INTO devices "
               "(mac_address, x_coord, y_coord, z_coord, global_loc_id, floor, loc_type) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s);")
	cursor.execute(add_device, data_device)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;


def device_init():
	'''
	Sets all devices to inactive
	
	'''	
	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root', password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_device = ("UPDATE devices SET status=-1;")
	cursor.execute(add_device)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;

def insert_device_capabilities(data_device):
	'''
	Inserts device capabilities in the database
	Args:
		data_device: the data used for inserting
	'''
	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root', password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()
	list_device = list(data_device)
	list_device.append(data_device[1])
	list_device.append(data_device[2])
	data_device = tuple(list_device)

	add_device = ("INSERT INTO devices (mac_address, uuid, chan_capab) "
               "VALUES(%s, %s, %s) "
               "ON DUPLICATE KEY UPDATE uuid=%s, chan_capab=%s;")
	cursor.execute(add_device, data_device)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;

def update_device_status(data_device):
	'''
	Inserts device status in the database
	Args:
		data_device: the data used for inserting
	'''
	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root', password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	list_device = list(data_device)
	list_device.append(data_device[1])
	list_device.append(data_device[2])
	list_device.append(data_device[3])
	list_device.append(data_device[4])
	list_device.append(data_device[5])
	list_device.append(data_device[6])
	list_device.append(data_device[7])
	data_device = tuple(list_device)

	add_device = ("INSERT INTO devices (mac_address, status, mode, power, ssid, active_channel, active_channel_sup, ap_mac_address) "
               "VALUES(%s, %s, %s, %s, %s, %s, %s, %s) "
               "ON DUPLICATE KEY UPDATE "
	       "status=%s, mode=%s, power=%s, ssid=%s, active_channel=%s, active_channel_sup=%s, ap_mac_address=%s;")
	cursor.execute(add_device, data_device)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;

def insert_duty_cycle(data_duty_cycle):
	'''
	Inserts duty cycle information in the database
	Args:
		data_duty_cycle: the data used for inserting
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_duty_cycle = ("INSERT IGNORE INTO duty_cycle "
               "(rx_mac_address, value, timestamp, channel) "
               "VALUES (%s, %s, %s, %s)")
	cursor.execute(add_duty_cycle, data_duty_cycle)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;

def insert_tx_location(data_tx_location):
	'''
	Inserts localized tx information in the database
	Args:
		data_tx_location: the data used for inserting
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_tx_location = ("INSERT INTO estimated_locations "
               "(tx_mac_address, x_coord, y_coord, global_loc_id, floor, timestamp, channel, tx_power) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
	cursor.execute(add_tx_location, data_tx_location)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;


def insert_propagation_model(data_prop_model):
	'''
	Inserts propagation model information in the database
	Args:
		data_prop_model: the data used for inserting
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_prop_model = ("INSERT INTO propagation_model "
               "(L0, alpha, sigma, d0, timestamp, channel) "
               "VALUES (%s, %s, %s, %s, %s, %s)")
	cursor.execute(add_prop_model, data_prop_model)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;


def insert_rssi_measurement(data_rssi):
	'''
	Inserts rssi measurement information in the database
	Args:
		data_rssi: the data used for inserting
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_rssi = ("INSERT IGNORE INTO rssi_meas "
               "(tx_mac_address, rx_mac_address, value, timestamp, signal_type, bw_mode, active_channel, active_channel_sup) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
	cursor.execute(add_rssi, data_rssi)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;



def insert_global_location(data_location):
	'''
	Inserts global location information in the database
	Args:
		data_location: the data used for inserting
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_location = ("INSERT INTO global_location "
               "(name_identifier, x_coord, y_coord, z_coord) "
               "VALUES (%s, %s, %s, %s)")
	cursor.execute(add_location, data_location)

	# Make sure data is committed to the database
	cnx.commit()

	query = ("select id from global_location where name_identifier = '" + data_location[0] + "' order by id DESC limit 1;")

	cursor.execute(query)
	locid = cursor.fetchone()[0]

	cursor.close()
	cnx.close()
	return locid;


def insert_ap_statistics(ap_data):
	'''
	Inserts AP statistics information in the database
	Args:
		ap_data: the data used for inserting
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_ap_statistics = ("INSERT IGNORE INTO ap_statistics "
               "(ap_mac_address, total_tx_retries, total_tx_failed, "
	       "total_tx_throughput, total_rx_throughput, total_tx_activity, total_rx_activity, timestamp) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
	cursor.execute(add_ap_statistics, ap_data)

	# Make sure data is committed to the database
	cnx.commit()

	cursor.close()
	cnx.close()
	return;

def insert_link_statistics(link_data):
	'''
	Inserts link statistics information in the database
	Args:
		link_data: the data used for inserting
	'''

	host_env = os.getenv('MYSQL_ENV', 'localhost')
	cnx = mysql.connector.connect(user='root',password='rem', host=host_env,database='remdb')
	cursor = cnx.cursor()

	add_link_statistics = ("INSERT IGNORE INTO link_statistics "
               "(tx_mac_address, rx_mac_address, rssi, tx_retries, tx_failed, "
	       "tx_rate, rx_rate, tx_throughput, rx_throughput, tx_activity, rx_activity, timestamp) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s')")
	print(add_link_statistics, link_data)
	result = cursor.execute(add_link_statistics, link_data)
	print(result)

	# Make sure data is committed to the database
	result = cnx.commit()
	print(result)

	cursor.close()
	cnx.close()
	return;



