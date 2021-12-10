#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
# import libraries
from os import listdir
from os.path import join

import numpy
import pandas as pd
from pydicom import dcmread

import env

# data path
src = env.properties['patientsFolder']

# get content of dictionary
roi_information = pd.read_excel(env.properties['roiExcel'], engine='openpyxl')

rtstruct_names = roi_information["Names"].values.tolist()  # standard names
# new names
new_names = [
    '' if x is numpy.nan else x for x in roi_information["New name"].values.tolist()]

valid_names = list(filter(lambda x: x != '', new_names))
if (len(valid_names) > len(set(valid_names))):
    raise Exception('There are duplicates in the new names list: ' + new_names)

new_name_mapping = dict(zip(rtstruct_names, new_names))


for patient in listdir(src):
    if (env.properties['patientFilter'] and patient not in env.properties['patientFilter']):
        continue
    # get patient file
    rois_patient = []
    patient_folder = join(src, patient)
    for f in listdir(patient_folder):
        if 'RTSTRUCT' in f:  # verify that it is a DICOM image
            dcm_struct = dcmread(join(patient_folder, f))
            for roi in dcm_struct.StructureSetROISequence:
                name = roi.ROIName
                if new_name_mapping[name] != '':
                    roi.ROIName = new_name_mapping[name]
            dcm_struct.save_as(join(patient_folder, 'ValidROIs_' + f))
