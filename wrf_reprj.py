#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 14:05:27 2019

@author: caleb.pan
"""
"""
THIS SCRIPT IS USED TO EXTRACT BANDS FROM A MULTI-BAND NETCDF FILE CONTAINING
DAILY AVERAGE 2M TEMPERATURE DERIVED USING THE WEATHER RESEARCH AND FORECASTING
(WRF) MODEL AND DOWNSCALED USING ERA-INTERIM REANALYSIS.

ONCE THE BANDS ARE EXTRACTED WE WANT TO EXPORT IT TO A GEOTIFF. THIS REQURES
TWO KEY STEPS 1) CONVERTING THE DEFINED PROJ4 TO WKT AND 2) CREATING THE
OUTPUT TIF AND ASSIGNING THE ARRAY

THE DOWNSCALED CLIMATE DATA FOR ALASKA CAN BE DOWNLOADED FROM THE AWS FTP 
HERE: 
http://ckan.snap.uaf.edu/dataset/historical-and-projected-dynamically-\
downscaled-climate-data-for-the-state-of-alaska-and-surrou
"""  


# =============================================================================
# IMPORT YOUR LIBRARIES
# =============================================================================
import gdal
from osgeo import osr

# =============================================================================
# DEFINE ANY PROCEDURES. THESE PROCEDURES HELP GETTING GEOTRANSFORM, ARRAY 
# DIMENSIONS AND CONVERTING NUMBERS TO A 3 DIGIT STRINGS
# =============================================================================
def getgeo(openfile):
    opentif = gdal.Open(openfile)
    geo = opentif.GetGeoTransform()
    return geo

def getdim(openfile):
    opentif = gdal.Open(openfile)
    wide = opentif.RasterXSize
    high = opentif.RasterYSize
    return wide, high

def getday(day):
    if day<10:
        newday = '00' + str(day)
    elif (day >= 10) & (day < 100):
        newday = '0' + str(day)
    else:
        newday = str(day)   
    return newday

# =============================================================================
# SET ROOT DIRECTORY
# =============================================================================
root = '/anx_lagr2/caleb/GitHub/wrf/data/'

# =============================================================================
# The netcdf's spatial refernce is provided as a simple PROJ4 string. In order
# to assign this spatial reference to the exported geotif, it needs to be 
# converted into WKT - which is achieved using osgeo.
# =============================================================================
prj4 = '+proj=stere +ellps = WGS84 +lat_0=90 +lat_ts=64 +lon_0=-152 +k=1 +x_0=0 +y_0=0 +a=6370000 +b=6370000 +units=m +no_defs'
srs = osr.SpatialReference()
srs.ImportFromProj4(prj4)

# =============================================================================
# prj is the new projection information which will be set to the exported tif
# =============================================================================
prj = srs.ExportToWkt()

cdf = root + 't2_daily_wrf_ERA-Interim_historical_1989.nc' #set the netcdf filename
openfile = gdal.Open('NETCDF:' + cdf + ':t2') #open the netcdf air temperature variable (t2)

doy = 35 ##input the day of year you want to to convert (can be applied in a loop)
day = getday(doy)
band = openfile.GetRasterBand(day) ##each band number corresponds to a doy
array = band.ReadAsArray()

dim = getdim(cdf)
geo = getgeo(cdf)
driver = gdal.GetDriverByName('GTiff')
outfile = root + 't2_daily_wrf_ERA-Interim_historical_1989' + day + '.tif'
dst = driver.Create(outfile, dim[0], dim[1], 1, gdal.GDT_Int16)
dst.SetProjection(prj) #assign the wkt projection
dst.SetGeoTransform(geo)
dst.GetRasterBand(1).WriteArray(array)
print 'exporting ' + outfile
del driver, dst
        
