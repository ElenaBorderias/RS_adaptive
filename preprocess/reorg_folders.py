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
from pydicom.dataset import Dataset

# data path
src = r"X:\Elena_test"
# parse data folder
roi_names = []

"""
##Margeries code
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
"""

# loop over patients
for patient in os.listdir(src):
    # get patient file
    srcfolder = os.path.join(src,patient)
    
    if not patient[0] == '.':
        ctfolder = os.path.join(srcfolder,'CT')
        cbctfolder = os.path.join(srcfolder,'CBCT')
        if not os.path.exists(ctfolder):
            os.mkdir(ctfolder)
        if not os.path.exists(cbctfolder):
            os.mkdir(cbctfolder)
        # get useful info
        ct_uids = []
        ct_zcoord = []
        ct_sliceLoc = []
        ct_InstanceNbr = []
        # loop over files in patient
        for f in os.listdir(srcfolder):
            if '.dcm' in f:

                dcm_header = pydicom.read_file(os.path.join(srcfolder,f),force = True)
                manufacturer = dcm_header.Manufacturer
                modality = dcm_header.Modality
                SeriesInstanceUID = dcm_header.SeriesInstanceUID
                station_name = dcm_header.StationName
                n_cbct_folder = os.path.join(cbctfolder,SeriesInstanceUID)

                old_name = os.path.join(srcfolder,f)

                if not os.path.exists(n_cbct_folder):
                    os.mkdir(n_cbct_folder)
                
                if modality == 'CT':


                    if manufacturer == 'Varian Medical Systems' and station_name == "HALCYON_SPO":
                        destination = n_cbct_folder
                        source = os.path.join(srcfolder,f)
                        shutil.move(source, destination)

                    elif manufacturer == 'TOSHIBA':
                        destination = ctfolder
                        source = os.path.join(srcfolder,f)
                        shutil.move(source, destination)

                elif modality == 'RTSTRUCT':
                    new_name_rtstruct = os.path.join(srcfolder,"RTSTRUCT_"+f)
                    os.rename(old_name,new_name_rtstruct)
                    print("RTStruct is in the DB")
                
                elif modality == 'RTPLAN':
                    new_name_plan = os.path.join(srcfolder,"RTPLAN_"+f)
                    os.rename(old_name,new_name_plan)
                    print("Plan is in the DB")

                elif modality == 'RTDOSE':
                    new_name_dose = os.path.join(srcfolder,"RTDOSE_"+f)
                    os.rename(old_name,new_name_dose)
                    print("Clincal doose is in the DB")
                
                else:
                    print(f)
                    print("This dicom is has not a valid modality in the dicom header")

                
