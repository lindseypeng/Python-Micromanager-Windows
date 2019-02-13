#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 14:52:30 2019

@author: lindsey
"""



#Environment setup instructions: https://micro-manager.org/wiki/Using_the_Micro-Manager_python_library
#import MMCorePy #load MicroManager for device control
#import matplotlib.pyplot as plt
import time
import pandas as pd
import numpy as np
import os
import argparse
import datetime
import tifffile
########################################################################################
## load the varaibles from argument parser
########################################################################################
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True,help="path to input csv file")
ap.add_argument("-o", "--output", required=True,help="path to save images")
args = vars(ap.parse_args())
folderread = args["input"]
foldersave = args["output"]
placeread=folderread+"threeDPositions{}.csv"
#load camera and set it up
mmc = MMCorePy.CMMCore()
mmc.loadDevice('Camera', 'ThorlabsUSBCamera', 'ThorCam')
mmc.initializeAllDevices()
mmc.setCameraDevice('Camera')
mmc.setExposure(40)##set exposure rate in ms
startcsv=0
endcsv=299
interval=5##every 25 frames, each file has 5 frames
rangenum=np.arange(startcsv,endcsv)
initialframes=12
timestamps=pd.DataFrame()
########################################################################################
## start with saving images for 1 hour
########################################################################################
starting=str(datetime.datetime.now())
for i in np.arange(initialframes):
    f="{04d}".format(i)
    mmc.snapImage()
    img = mmc.getImage() #this is numpy array, by the way
    now = time.time()
    tifffile.imsave(foldersave+"/img_00000{}_Default_000.tif".format(f))
#    plt.imsave(foldersave+"/frame{}".format(i),img)
    time.sleep(300)##save image every 5 minutes 
    timestamp=pd.DataFrame( {'frame':i,'elapsedtime(s)':now},index=[str(i)])
    timestamps=timestamps.append(timestamp,ignore_index=True)
########################################################################################
## start with adaptive image c apture
########################################################################################
maxframes=5000
for i in np.arange(initialframes,maxframes): 
    f="{04d}".format(i)
    mmc.snapImage()
    img = mmc.getImage() #this is numpy array, by the way
    now = time.time()
    tifffile.imsave(foldersave+"/img_00000{}_Default_000.tif".format(f))
    timestamp=pd.DataFrame( {'frame':i,'elapsedtime(s)':now},index=[str(i)])
    timestamps=timestamps.append(timestamp,ignore_index=True)
    current=placeread.format(i)
    if os.path.exists(current)==False:
        time.sleep(1200)#give enough time to make sure that the file exist
        pass##continue with this file
    else:
        currentfile=pd.read_csv(current)
        currentporosity=np.average(np.array(currentfile.porosity))
        if currentporosity <= 1.5:
            time.sleep(300)##capture only every 5 minutes for no activity
        elif (currentporosity >=1.5 and currentporosity <5):
            time.sleep(10)##capture every 10 seconds + overhead, for 3 hours its 1000 frames
        elif (currentporosity >=5 and currentporosity <10):
            time.sleep(30)##capture every 1 seconds + overhead, for 3 hours its 360 frames
        elif (currentporosity >=10 and currentporosity <15 ):
            time.sleep(120)##every minute , 120 frames for 4 hours
        elif (currentporosity >=15 and currentporosity <20 ):
            time.sleep(300)##capture only every 5minutes 
        elif (currentporosity >=20 and currentporosity <33 ):
            time.sleep(600)##capture only every 10minutes 
        elif (currentporosity >= 33):
            break
    
    
            
timestamps.to_csv(foldersave+"/"+starting+"timestamp.csv")

