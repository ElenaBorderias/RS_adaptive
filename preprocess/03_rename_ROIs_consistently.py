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
from pydicom import dcmread

# data path
src = r"X:\Elena_test"
# parse data folder
roi_names = []
n_times = []
n_patients = []

# get content of dictionary
dict_path = 'Y:\Elena\RaySearch_internship\HAN_IMPT_dictionary_not_all_caps.xlsx'
dictionary = pd.read_excel(dict_path, engine='openpyxl')

rtstruct_names = dictionary["Names"] # standard names
new_names = dictionary["New name"] # new names 


for patient in os.listdir(src):
    # get patient file
    rois_patient = []
    srcfolder = os.path.join(src, patient)
    for f in os.listdir(srcfolder):
        if 'RTSTRUCT' in f:  # verify that it is a DICOM image
            dcm_struct = dcmread(os.path.join(src, patient, f))
            for roi in dcm_struct.StructureSetROISequence:
                name = roi.ROIName
                if name in new_names:
                    roi_index = roi_names.index(name)
                    roi.ROIName = new_names[roi_index]
            dcm_struct.save_as(os.path.join(src, patient, f))
            
        

