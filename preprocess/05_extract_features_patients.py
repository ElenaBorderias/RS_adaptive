#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
# import libraries
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import pandas as pd
import pydicom
import numpy as np

from scipy.signal import argrelextrema
from findpeaks import findpeaks

from sklearn import mixture


#import env

# data path
src = "X:\\Elena_test"
excel_path = "X:\\log_file_modified.xlsx"
export_excel_path = "X:\\features.xlsx"
export_hist_path = "X:\\dose_histograms"
anon_data_full = pd.read_excel(excel_path, engine='openpyxl')

features = anon_data_full[['Anon name', 'StructureSetLabel']]

features.columns = ['name', 'localisation']

n_cbcts = []
n_frac = []
prescriptuon = []
max_dose = []

#check_pat = []
dose_peaks = []

patient_list = anon_data_full['Anon name'].to_numpy()
patient_list =  patient_list.tolist()

for patient in patient_list:
    # # get patient file
    # if (env.properties['patientFilter'] and patient not in env.properties['patientFilter']):
    #     continue
    patient_folder = join(src, patient)

    # cbcts
    number_of_cbcts = len(listdir(join(patient_folder, 'CBCT')))
    n_cbcts.append(number_of_cbcts)

    # prescription

    for f in listdir(patient_folder):
        if isfile(join(patient_folder, f)) and 'RTDOSE' in f:  # verify that it is a DICOM image
            
            
            dcm = pydicom.read_file(join(src, patient, f))
            dose = dcm.pixel_array * dcm.DoseGridScaling  # dose in  grays

            max_dose.append(dose.max())
            ##check_pat.append(patient)

            hist, bins = np.histogram(dose, bins=30, range=(40, 72), normed=None, weights=None, density=None)  # every 2 Gy is 16 bins
            peaks_index = argrelextrema(hist, np.greater)
            
            
            dose_peaks_per_pat = np.round(bins[peaks_index],2).tolist()
            
            print(dose_peaks_per_pat)
            
            dose_peaks.append(dose_peaks_per_pat)
            
            width = np.diff(bins)
            center = (bins[:-1] + bins[1:]) / 2
            fig, ax = plt.subplots(figsize=(30, 5))
            ax.bar(center, hist, align='center', width=width)
            ax.set_xticks(bins)
            ax.set_title(patient)

            fig.savefig(join(export_hist_path,patient+".png"))

features['n_cbcts'] = n_cbcts
features['dose max'] = max_dose
features['dose_peaks'] = dose_peaks
features['prescription'] = ""

# =============================================================================
#             for dcm_struct in dcm.StructureSetROISequence:
#                 name = dcm_struct.ROIName
#                 if name not in roi_names:
#                     roi_names.append(name)
#                     n_times.append(1)
#                     n_patients.append([patient])
#                 else:
#                     roi_index = roi_names.index(name)
#                     n_times[roi_index] = n_times[roi_index] + 1
#                     n_patients[roi_index].append(patient)
# =============================================================================


features.to_excel(export_excel_path, index=False)
