#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
# import libraries
from os import listdir
from os.path import isfile, join

import pandas as pd
import pydicom

import env

# data path
src = env.properties['patientsFolder']
# parse data folder
roi_names = []
n_times = []
n_patients = []

# Margeries code
roi_names = []
for patient in listdir(src):
    # get patient file
    if (env.properties['patientFilter'] and patient not in env.properties['patientFilter']):
        continue
    rois_patient = []
    patient_folder = join(src, patient)
    for f in listdir(patient_folder):
        if isfile(join(patient_folder, f)) and 'RTSTRUCT' in f:  # verify that it is a DICOM image
            dcm = pydicom.read_file(join(src, patient, f))
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

#print(roi_names[0], n_patients[0])

# write to excel
if (not roi_names):
    raise Exception("ROI names not read")

df = pd.DataFrame({'#': n_times, 'patients': n_patients,
                  'Names': roi_names, 'New name': ['']*len(roi_names)})

df.to_excel(env.properties['roiExcel'], index=False)
