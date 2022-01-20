#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
# import libraries

import pandas as pd
import env

# data path
excel_path = r"X:\Elena_test\log_file_EB.xls"

# data path
src = env.properties['patientsFolder']

anon_data = pd.read_excel(excel_path)

def find_date(patient_name):


for patient in listdir(src):
    if (env.properties['patientFilter'] and patient not in env.properties['patientFilter']):
        continue
    anon_data_pat = anon_data[anon_data["Patient" == patient]]
