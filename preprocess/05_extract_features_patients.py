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
excel_path = "X:\\log_file.xlsx"
anon_data_full= pd.read_excel(excel_path, engine='openpyxl')

features = anon_data_full[['Anon name','Structure Set Label']]
features.columns = ['name', 'localisation']

n_cbcts = []
n_frac =  []
prescriptuon = []

for patient in listdir(src):
    # get patient file
    if (env.properties['patientFilter'] and patient not in env.properties['patientFilter']):
        continue
    patient_folder = join(src, patient)

    #cbcts
    number_of_cbcts = len(listdir(join(patient_folder, 'CBCT')))
    n_cbcts.append(number_of_cbcts)

    #nfractions

    #prescription
    
    for f in listdir(patient_folder):
        if isfile(join(patient_folder, f)) and 'RTDOSE' in f:  # verify that it is a DICOM image
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

features.to_excel(env.properties['featuresExcel'], index=False)
