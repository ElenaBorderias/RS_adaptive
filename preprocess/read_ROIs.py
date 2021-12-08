#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
# import libraries
import os 
import shutil
import pydicom
import pandas as pd
import numpy as np
from pydicom.dataset import Dataset

# data path
src = r"X:\Elena_test"
# parse data folder
roi_names = []

##Margeries code
roi_names = []
for patient in os.listdir(src):
    # get patient file
    srcfolder = os.path.join(src,patient)
    for f in os.listdir(srcfolder):
        if 'RTSTRUCT' in j: # verify that it is a DICOM image
            dcm = pydicom.read_file(os.path.join(src,f))
            if dcm.Modality == 'RTSTRUCT':
                for dcm_struct in dcm.StructureSetROISequence: 
                    roi_names.append(dcm_struct.ROIName)
                    print(dcm_struct.ROIName)

# convert all names to uppercase to avoid repetitions
# for i in range(len(roi_names)):
#    roi_names[i] = roi_names[i].upper()
    
# get unique names
roi_names = np.unique(roi_names)
    
# write to excel
df=pd.DataFrame({'Names':roi_names,
                 'Needed or not':np.zeros(len(roi_names)),
                 'New name':np.zeros(len(roi_names))}) 

df.to_excel(r'Y:\Elena\RaySearch_internship\HAN_IMPT_dictionary_not_all_caps.xlsx',index = False)