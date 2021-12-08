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
n_times = []
n_patients = []

# Margeries code
roi_names = []
for patient in os.listdir(src):
    # get patient file
    rois_patient = []
    srcfolder = os.path.join(src, patient)
    for f in os.listdir(srcfolder):
        if 'RTSTRUCT' in f:  # verify that it is a DICOM image
            dcm = pydicom.read_file(os.path.join(src, patient, f))
            for dcm_struct in dcm.StructureSetROISequence:
                name = dcm_struct.ROIName
                if name not in roi_names:
                    roi_names.append(name)
                    n_times.append(1)
                    n_patients.append([patient])
                else:
                    roi_index = roi_names.index(name)
                    n_times[roi_index] = n_times[roi_index] + 1
                    n_patients[roi_index].append(patient)

print(roi_names[0],n_patients[0])

# write to excel
df = pd.DataFrame({'#': n_times,'patients': n_patients,'Names': roi_names, 'New name': np.zeros(len(roi_names))})

df.to_excel(r'Y:\Elena\RaySearch_internship\HAN_IMPT_dictionary_not_all_caps.xlsx', index=False)
