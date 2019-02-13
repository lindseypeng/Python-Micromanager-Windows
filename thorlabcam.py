
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 14:52:30 2019

@author: lindsey
"""



#Environment setup instructions: https://micro-manager.org/wiki/Using_the_Micro-Manager_python_library
#import MMCorePy #load MicroManager for device control
import matplotlib.pyplot as plt
import time
import pandas as pd
import numpy as np
import os
import argparse
import datetime

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
startcsv=0
endcsv=299
interval=5##every 25 frames, each file has 5 frames
rangenum=np.arange(startcsv,endcsv)
initialframes=30
timestamps=pd.DataFrame()
########################################################################################
## start with saving images every 30 seconds for 30frames
########################################################################################
starting=str(datetime.datetime.now())
for i in np.arange(initialframes):
    mmc.setExposure(40) #ms
    mmc.snapImage()
    img = mmc.getImage() #this is numpy array, by the way
    now = time.time()
    plt.imsave(foldersave+"/frame{}".format(i),img)
    time.sleep(30)##save image every 30 seconds
    timestamp=pd.DataFrame( {'frame':i,'elapsedtime(s)':now},index=[str(i)])
    timestamps=timestamps.append(threeDposition,ignore_index=True)
########################################################################################
## start with adaptive image c apture
########################################################################################
infiniteframes=50000
for i in np.arange(infiniteframes): 
    mmc.setExposure(40) #ms
    mmc.snapImage()
    img = mmc.getImage() #this is numpy array, by the way
    now = time.time()
    plt.imsave(foldersave+"/frame{}".format(i),img)
    timestamp=pd.DataFrame( {'frame':i,'elapsedtime(s)':now},index=[str(i)])
    timestamps=timestamps.append(threeDposition,ignore_index=True)
    current=placeread.format(i)
    if os.path.exists(current)==False:
        time.sleep(1200)#give enough time to make sure that the file exist
        pass##continue with this file
    else:
        currentfile=pd.read_csv(current)
        currentporosity=np.average(np.array(currentfile.porosity))
        if currentporosity <= 2:
            time.sleep(150)##capture only every 5 minutes for no activity
        elif (currentporosity >=2 and currentporosity <10):
            time.sleep(10)##capture every 1 seconds + overhead
        elif (currentporosity >=10 and currentporosity <15 ):
            time.sleep(30)
        elif (currentporosity>=15 and < 32):
            time.sleep(300)##capture only every 10 minutes 
        elif (currentporosity >= 32):
            break
    
    
            
timestamps.to_csv(foldersave+"/"+starting+"timestamp.csv")
