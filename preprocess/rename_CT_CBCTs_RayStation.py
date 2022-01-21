#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
from connect import *

anon_path = "C:\Elena\log_file_EB.xls" 
patient = get_current("Patient")
case = get_current("Case")

anon_info = pd.read_excel(anon_path)
anon_info_patient = anon_info[anon_info["Patient"] == patient.Name]
print(anon_info_patient)

for exam in case.Examinations:
    exam.Series[0].ImportedDicomUID
