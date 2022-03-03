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
import json
from pydicom.dataset import Dataset

_f = open('preprocess/env.json')
properties = json.load(_f)
_f.close()

# data path
src = properties['patientsFolder']
# parse data folder
roi_names = []


def createFolder(folder, force=False):
    if not os.path.exists(folder):
        os.mkdir(folder)
    elif(not force):
        raise Exception('folder: ' + folder + ' already exists.')


def storePreprocess(patient_folder, dcm_file):
    with open(os.path.join(patient_folder, 'reorganise_folders.txt'), 'a+') as f:
        f.write(dcm_file)
        f.write('\n')


def getPreviousRun(patient_folder):
    processed_files = []
    log_file = os.path.join(patient_folder, 'reorganise_folders.txt')
    if not os.path.exists(log_file):
        return processed_files
    with open(os.path.join(patient_folder, 'reorganise_folders.txt'), 'r') as f:
        processed_files = [line.rstrip('\n') for line in f]
    return processed_files


# loop over patients
for patient in os.listdir(src):
    patient_folder = os.path.join(src, patient)

    if (os.path.isdir(patient_folder) and (not properties['patientFilter'] or patient in properties['patientFilter'])):
        print(patient)
        processed_files = getPreviousRun(patient_folder)
        ct_folder = os.path.join(patient_folder, 'CT')
        cbct_folder = os.path.join(patient_folder, 'CBCT')
        other_ct_folder = os.path.join(patient_folder, 'Other_CT')


        createFolder(ct_folder, force=True)
        createFolder(cbct_folder, force=True)
        # get useful info
        ct_uids = []
        ct_zcoord = []
        ct_sliceLoc = []
        ct_InstanceNbr = []
        # loop over files in patient
        for f in os.listdir(patient_folder):
            dicom_file_path = os.path.join(patient_folder, f)
            if os.path.isfile(dicom_file_path) and '.dcm' in f and f not in processed_files:
                
                dcm_header = pydicom.read_file(dicom_file_path, force=True)
                manufacturer = dcm_header.Manufacturer
                modality = dcm_header.Modality
                SeriesInstanceUID = dcm_header.SeriesInstanceUID
                print('processing file: ' + f)
                print('Modality: ' + modality)
                print('Manufacturer: '   + manufacturer)
                try: 
                    station_name = dcm_header.StationName
                except AttributeError  as err:
                    print(err)
                    continue
                if modality == 'CT':
                    if manufacturer == 'Varian Medical Systems' and station_name == "HALCYON_SPO":
                        n_cbct_folder = os.path.join(
                            cbct_folder, SeriesInstanceUID)
                        createFolder(n_cbct_folder, force=True)
                        destination = n_cbct_folder
                        shutil.move(dicom_file_path, destination)
                        storePreprocess(patient_folder, f)

                    elif manufacturer == 'TOSHIBA':
                        destination = ct_folder
                        shutil.move(dicom_file_path, destination)
                        storePreprocess(patient_folder, f)
                    
                    else:
                        createFolder(other_ct_folder, force=True)
                        destination = other_ct_folder
                        shutil.move(dicom_file_path, destination)
                        storePreprocess(patient_folder, f)

                elif modality == 'RTSTRUCT':
                    new_name_rtstruct = os.path.join(
                        patient_folder, "RTSTRUCT_"+f)
                    os.rename(dicom_file_path, new_name_rtstruct)
                    storePreprocess(patient_folder, "RTSTRUCT_"+f)

                elif modality == 'RTPLAN':
                    new_name_plan = os.path.join(
                        patient_folder, "RTPLAN_"+f)
                    os.rename(dicom_file_path, new_name_plan)
                    storePreprocess(patient_folder, "RTPLAN_"+f)

                elif modality == 'RTDOSE':
                    new_name_dose = os.path.join(
                        patient_folder, "RTDOSE_"+f)
                    os.rename(dicom_file_path, new_name_dose)
                    storePreprocess(patient_folder, "RTDOSE_"+f)

                else:
                    print(f)
                    print(
                        "This dicom is has not a valid modality in the dicom header")
