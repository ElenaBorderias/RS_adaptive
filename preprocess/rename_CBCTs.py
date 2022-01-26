#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
# import libraries

from os.path import join, isdir
from os import listdir, rename
import openpyxl
import pandas as pd

excel_path = "X:\\log_file_EB.xlsx"
patient_path = "X:\\Elena_test"
anon_data_full= pd.read_excel(excel_path, engine='openpyxl', converters={'AcquisitionDate':str,'AcquisitionTime':str})
anon_data= anon_data_full.iloc[0:len(anon_data_full),0:15]

series_order = anon_data[['Anon name','Manufacturer', 'Modality', 'SeriesInstanceUID', 'AcquisitionDate','AcquisitionTime']]
series_order.columns = ['name', 'man', 'modality', 'uid', 'date', 'time']
series_order['date-time'] = series_order['date'] + series_order['time']
series_order['date-time'] = pd.to_datetime(series_order['date-time'], format = '%Y%m%d%H%M%S',  exact=False)

series_ordered = series_order.sort_values(by=['name','date-time'])
 
series_ordered = series_ordered[series_ordered['man'] == 'Varian Medical Systems']
series_ordered = series_ordered[series_ordered['modality'] == 'CT']


#series_order['date'].apply(lambda x: pd.to_datetime(x, format='%Y%m%d'))

for patient in listdir(patient_path):
    if patient == 'ANON1':
        anon_info = series_ordered[series_ordered['name'] == patient]
        i = 0
        for index, cbct_row in anon_info.iterrows():
            print(patient + ' ' + str(i).zfill(2) + ' ' + str(cbct_row['uid']))
            i += 1
            if isdir(join(patient_path, patient, 'CBCT', cbct_row['uid'])):
                print('hello')
                rename(join(patient_path, patient, 'CBCT', cbct_row['uid']), join(patient_path, patient, 'CBCT', str(i).zfill(2) + '_' + cbct_row['uid']))
        
# =============================================================================
# for patient in listdir(patient_path):
#     anon_data_pat = anon_data[anon_data["Anon name"] == patient and anon_data["Manufacturer"] == 'Varian  Medical System' and anon_data[]]
#     anon_data_pat_sorted=anon_data_pat.sort_values(by=["AcquisitionDate"])
#     for cbct_instance, i in enumerate(listdir(join(patient_path,patient,"CBCT"))):
# =============================================================================
        
        