
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""

from connect import get_current
import numpy as np

def get_displacement_field(original_DIR_reg):
  
  deformationGrid = original_DIR_reg.DeformationGrid
  nrOfVectors = (deformationGrid.NrVoxels.x + 1) * (deformationGrid.NrVoxels.y + 1) * (deformationGrid.NrVoxels.z + 1) 
  data = original_DIR_reg.DeformationMatrix

  #indices = range(0, nrOfVectors)
  #coordX = array('d',[System.BitConverter.ToDouble(data, i * 3 * 8) for i in indices])
  #coordY = array('d',[System.BitConverter.ToDouble(data, i * 3 * 8 + 8) for i in indices])
  #coordZ = array('d',[System.BitConverter.ToDouble(data, i * 3 * 8 + 16) for i in indices])
  
  disp_field = len(data)*[0]
  disp_field = bytearray(disp_field)
  return disp_field


patient = get_current("Patient")
case = get_current("Case")

dir_reg = patient.Cases[0].StructureRegistrations[4]
displacement_field = get_displacement_field(dir_reg)

#dir_reg.SetDisplacementField(DisplacementField = displacement_field)

dose_to_map = case.TreatmentPlans["ML_IMPT_plan"].TreatmentCourse.TotalDose
ref_dose_grid = case.TreatmentPlans["1_Mim_CBCT 02"].PlanOptimizations[0].OptimizationReferenceDose.InDoseGrid

case.MapDose(FractionNumber=0,SetTotalDoseEstimateReference=False,
            DoseDistribution=dose_to_map, StructureRegistration=dir_reg,ReferenceDoseGrid=ref_dose_grid)
"""
MapDose(..)
  Action for mapping dose from the target examination of the 
  registration to the reference examination of the registration.
  Note that it is possible to map a dose that has already been 
  mapped with the same registration.
  This will create two evaluation doses with the same properties.
  Parameters:
    FractionNumber - The fraction number of the dose 
      distribution.
      Default is zero.
    SetTotalDoseEstimateReference - Indicates if total dose 
      estimate reference should be set.
      Default is false.
    DoseDistribution - The dose distribution to map.
    StructureRegistration - The deformable registration to be 
      used for the dose mapping.
      The dose distribution must be defined on the target 
      examination of this registration.
    ReferenceDoseGrid - [NOT CLINICAL]
      The reference dose grid to which the dose will be mapped.
      If null, the dose will be deformed within its current dose grid. """