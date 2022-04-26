#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
from pyexpat import model
from connect import get_current
from genericpath import exists
import time
import SimpleITK as sitk
import numpy as np

case = get_current('Case')
patient = get_current('Patient')

all_rois = case.PatientModel.RegionsOfInterest
roi_names = [x.Name for x in all_rois]

for roi in roi_names:
    if roi.endswith('(1)') and not roi.startswith('eval_'):
        print(roi)
        #delete
        case.PatientModel.RegionsOfInterest[roi].DeleteRoi()
    if roi.endswith('(2)') and not roi.startswith('eval_'):
        print(roi)
        #delete
        case.PatientModel.RegionsOfInterest[roi].DeleteRoi()

patient.Save()



