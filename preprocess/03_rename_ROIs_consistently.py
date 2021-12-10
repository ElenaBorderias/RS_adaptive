#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
import ast
# import libraries
from os import listdir
from os.path import join

import numpy
import pandas as pd
from pydicom import dcmread

import env


def checkPatient(patient, new_names_for_patient):
    valid_names = list(filter(lambda x: x != '', new_names_for_patient))
    if (len(valid_names) > len(set(valid_names))):
        raise Exception(
            'Patient [' + patient + ']: there are duplicates in the new names list: ' + new_names_for_patient)

# patient_new_name struct looks like [[['ANON1','ANON2'], 'new_name']] output is dict with name per patient


def patientNamesPerPatient(patient_new_name):
    patients = {}
    for new_name_mapping in patient_new_name:
        for patient in new_name_mapping[0]:
            if not patients.get(patient):
                patients[patient] = []
            patients[patient].append(new_name_mapping[1])
    return patients


def checkPatientROINamesForDuplicates(patients, new_names):
    pateint_dict = patientNamesPerPatient(zip(patients, new_names))
    for patient, names in pateint_dict.items():
        checkPatient(patient, names)


# data path
src = env.properties['patientsFolder']

# get content of dictionary
roi_information = pd.read_excel(env.properties['roiExcel'], engine='openpyxl')

rtstruct_names = roi_information["Names"].values.tolist()  # standard names
patients = [ast.literal_eval(patient)
            for patient in roi_information["patients"].values.tolist()]
# new names
new_names = [
    '' if x is numpy.nan else x for x in roi_information["New name"].values.tolist()]

checkPatientROINamesForDuplicates(patients, new_names)

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
