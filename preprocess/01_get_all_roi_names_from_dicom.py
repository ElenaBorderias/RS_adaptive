#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: ana
"""
# import libraries
import os 
import numpy as np
import pydicom
import pandas as pd

# data path
# src=r"../HAN_PT_db"#DICOM"
#src = r"../VMAT_test/DICOM" #r'../NAS_database/train_data/HAN_XT/DICOM'
src = r"X:"
# parse data folder
roi_names = []
for i in sorted(os.listdir(src)):
    print(' ')
    print(i)
    if os.path.isdir(os.path.join(src,i)):
        for j in os.listdir(os.path.join(src,i)):
            print(j)
            if '.dcm' in j: # verify that it is a DICOM image
                dcm = pydicom.read_file(os.path.join(src,i,j))
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

df.to_excel(r'./HAN_VMAT_dictionary_not_all_caps.xlsx',index = False)

    