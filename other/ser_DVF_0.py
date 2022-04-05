#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""
from genericpath import exists
from connect import get_current
import time
import SimpleITK as sitk
import numpy as np


pct_name = "Corrected CBCT 16"
reference_ct_name = "pCT"

case = get_current("Case")
patient = get_current("Patient")

fileName = f"c:\\temp\\perturbedDIR_"+patient.Name+'_'+pct_name+".mhd"

def_reg_to_zero = case.Registrations[30].StructureRegistrations[0]

if not exists(fileName):
    def_reg_to_zero.ExportDeformableRegistrationAsMetaFile(MetaImageHeaderFileName = fileName)

DIR = sitk.ReadImage(fileName)
DVF = sitk.GetArrayFromImage(DIR)

print(DVF.shape,len(DVF), type(DVF),np.sum(DVF))

DVF_0 = np.zeros(DVF.shape)

print(DVF_0.shape,len(DVF_0), type(DVF_0),np.sum(DVF_0))

perturbedDIR = sitk.GetImageFromArray(DVF_0, isVector=True)
perturbedDIR.CopyInformation(DIR)

sitk.WriteImage(perturbedDIR, fileName)

#case.DeleteDeformableRegistration(StructureRegistration = case.Registrations[case.Registrations.Count-1].StructureRegistrations[0])
temp_reg_name = "Temp_reg_" + '16'
case.ImportDeformableRegistrationFromMetaImageFile(ReferenceExaminationName = pct_name,
                                                TargetExaminationName = reference_ct_name,
                                                DeformableRegistrationGroupName = temp_reg_name+'2',
                                                MetaImageHeaderFileName = fileName)
    