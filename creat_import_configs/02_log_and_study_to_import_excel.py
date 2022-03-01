

import json
from os import chdir, listdir
from os.path import isdir, join

import openpyxl
import pandas as pd

_f = open('creat_import_configs/env.json')
properties = json.load(_f)
_f.close()

patients_path = properties['patientsFolder']

chdir(patients_path)

excel_path = "log_file_EB.xlsx"
anon_data_full = pd.read_excel(excel_path, engine='openpyxl', converters={
                               'AcquisitionDate': str, 'AcquisitionTime': str})
anon_data = anon_data_full.iloc[0:len(anon_data_full), 0:15]

series_order = anon_data[['Anon name', 'Manufacturer', 'Modality',
                          'SeriesInstanceUID', 'AcquisitionDate', 'AcquisitionTime']]
series_order.columns = ['name', 'man',
                        'modality', 'series_uid', 'date', 'time']
series_order['date-time'] = series_order['date'] + series_order['time']
series_order['date-time'] = pd.to_datetime(
    series_order['date-time'], format='%Y%m%d%H%M%S',  exact=False)

study_uid_data = {}
with open('patient_study_uid.json') as json_file:
    study_uid_data = json.load(json_file)


study_df = []
for i, value in series_order['name'].items():
    print(i,value)
    study_df.append(study_uid_data.get(
        value, {'StudyInstanceUID': ''}).get('StudyInstanceUID', ''))

series_order['study_uid'] = pd.Series(study_df)

series_ordered = series_order.sort_values(by=['name', 'date-time'])

series_ordered.to_excel("import_list.xlsx", engine='openpyxl')
