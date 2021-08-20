#!/usr/bin/env python
# -*- coding: utf-8 -*-

from smbus import SMBus
import time
"""import os,sys
retval = os.getcwd()
path="BME280"
os.chdir(path)
retval = os.getcwd()
print("2",retval)"""

import BME280.bme280_sample as BME280

def get_data():
	t,p,h = BME280.readData()
	#d = BME280.makeJSON(t,p,h)
	return t,p,h

