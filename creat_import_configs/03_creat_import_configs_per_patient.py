

import json
from cmath import isnan
from os import chdir, listdir
from os.path import isdir, join

import openpyxl
import pandas as pd

patients_path = '/Users/comas/develop/elena/dicom_samples'
chdir(patients_path)

excel_path = "import_list.xlsx"
anon_data_full = pd.read_excel(excel_path, engine='openpyxl')

patient_info = {}

for index, patient_data in anon_data_full.iterrows():
    if patient_data['name'] not in patient_info:
        patient_info[patient_data['name']] = {}
    study_uid = patient_data['study_uid']
    if (pd.isna(study_uid)):
        study_uid = ''
    import_info = {'PatientID': patient_data['name'], 'StudyInstanceUID': study_uid,
                   'SeriesInstanceUID': patient_data['series_uid']}
    if (patient_data['man'] == 'TOSHIBA' and patient_data['modality'] == 'CT'):
        # ct processing
        print('ct processing')
        if 'ct' not in patient_info[patient_data['name']]:
            patient_info[patient_data['name']]['ct'] = []
        patient_info[patient_data['name']]['ct'].append(import_info)
    elif(patient_data['man'] == 'Varian Medical Systems' and patient_data['modality'] == 'CT'):
        print('cbct processing')
        if 'cbct' not in patient_info[patient_data['name']]:
            patient_info[patient_data['name']]['cbct'] = []
        patient_info[patient_data['name']]['cbct'].append(import_info)
    elif(patient_data['man'] == 'Varian Medical Systems' and patient_data['modality'] == 'RTDOSE'):
        patient_info[patient_data['name']]['rt_dose'] = import_info
    elif(patient_data['man'] == 'Varian Medical Systems' and patient_data['modality'] == 'RTSTRUCT'):
        patient_info[patient_data['name']]['rt_struct'] = import_info
    else:
        print('not processing', patient_data)


for patient in listdir():
    if (isdir(patient)):
        patient_path = join(patient)
        if (patient in ['ANON1']):
            with open(join(patient_path, "import_info.json"), "w") as outfile:
                json.dump(patient_info[patient], outfile)


with open("all_patient_import_info.json", "w") as outfile:
    json.dump(patient_info, outfile)
