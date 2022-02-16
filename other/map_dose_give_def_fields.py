
#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 20:34:46 2020

@author: elena
"""

from connect import get_current
import numpy as np

patient = get_current("Patient")
case = get_current("Case")

pct_name = "Corrected CBCT 02"
ml_plan_name = "2_Mim_CBCT 02"

reference_ct_name = "pCT"
cbct_name = "CBCT " + pct_name[-2:]
reference_plan = case.TreatmentPlans["ML_IMPT_plan"]

dose_to_map = reference_plan.TreatmentCourse.TotalDose

dgr = reference_plan.GetTotalDoseGrid()
CornerX = dgr.Corner.x
CornerY = dgr.Corner.y
CornerZ = dgr.Corner.z
VoxSizeX = dgr.VoxelSize.x
VoxSizeY = dgr.VoxelSize.y
VoxSizeZ = dgr.VoxelSize.z
NrVoxX = dgr.NrVoxels.x
NrVoxY = dgr.NrVoxels.y
NrVoxZ = dgr.NrVoxels.z

corner={'x': CornerX, 'y': CornerY, 'z': CornerZ}
vox_siz = {'x': VoxSizeX, 'y': VoxSizeY, 'z': VoxSizeZ}
nr_vox= {'x': NrVoxX, 'y': NrVoxY, 'z': NrVoxZ}

from_FOR = reference_plan.PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference
to_FOR = case.TreatmentPlans[ml_plan_name].PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference

new_corner = case.TransformPointFromFoRToFoR(FromFrameOfReference=from_FOR,ToFrameOfReference=to_FOR,Point=corner)

beam_set = case.TreatmentPlans[ml_plan_name].BeamSets[0]
beam_set.UpdateDoseGrid(Corner=new_corner,VoxelSize={'x': VoxSizeX,'y': VoxSizeY, 'z': VoxSizeZ},NumberOfVoxels={'x': NrVoxX, 'y': NrVoxY, 'z': NrVoxZ})

#set deformation field to 0
for reg in case.Registrations:
  for structure_reg in reg.StructureRegistrations:
    #print(structure_reg.Name)    
    #print(structure_reg.Name.startswith("DIR"))
    #print(structure_reg.FromExamination.Name, structure_reg.FromExamination.Name == cbct_name, cbct_name)
    #print(structure_reg.ToExamination.Name, structure_reg.ToExamination.Name == reference_ct_name, reference_ct_name)
  
    if structure_reg.Name.startswith("DIR") and structure_reg.FromExamination.Name == reference_ct_name and structure_reg.ToExamination.Name == cbct_name :
    	dir_reg = structure_reg

data = dir_reg.DeformationMatrix
disp_field = len(data)*[0]
disp_field = bytearray(disp_field)

from_FOR = case.TreatmentPlans["ML_IMPT_plan"].PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference
to_FOR = case.TreatmentPlans["2_Mim_CBCT 02"].PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference

rig_transf_DF = case.GetTotalTransformForExaminations(FromExamination=pct_name,ToExamination="pCT")
regid_transf_FoR = case.GetTotalTransformForExaminations(FromExamination=pct_name,ToExamination="pCT")

case.CreateNewDeformableRegistration(ReferenceExaminationName=pct_name,TargetExaminationName="pCT",
                                      RegistrationName="Reg_for_transf",RigidTransformDF=rig_transf_DF,
                                      RigidTransformFoR=regid_transf_FoR,FromFrameOfReference=from_FOR, ToFrameOfReference=to_FOR,
                                      GridCorner=corner, GridVoxelSize=vox_siz,NrOfVoxels=nr_vox,DisplacementField=disp_field)
"""

#map dose to converted image
dose_to_map = reference_plan.TreatmentCourse.TotalDose
ref_dose_grid = case.TreatmentPlans[ml_plan_name].PlanOptimizations[0].OptimizationReferenceDose.InDoseGrid

case.MapDose(FractionNumber=0,SetTotalDoseEstimateReference=False,
    DoseDistribution=dose_to_map, StructureRegistration=dir_reg,ReferenceDoseGrid=ref_dose_grid)
#set dose as predicted

#delete DIR
case.DeleteDeformableRegistration(StructureRegistration = dir_reg)

"""


""" def get_displacement_field(original_DIR_reg):
  
  deformationGrid = original_DIR_reg.DeformationGrid
  nrOfVectors = (deformationGrid.NrVoxels.x + 1) * (deformationGrid.NrVoxels.y + 1) * (deformationGrid.NrVoxels.z + 1) 
  data = original_DIR_reg.DeformationMatrix

  #indices = range(0, nrOfVectors)
  #coordX = array('d',[System.BitConverter.ToDouble(data, i * 3 * 8) for i in indices])
  #coordY = array('d',[System.BitConverter.ToDouble(data, i * 3 * 8 + 8) for i in indices])
  #coordZ = array('d',[System.BitConverter.ToDouble(data, i * 3 * 8 + 16) for i in indices])
  
  disp_field = len(data)*[0]

  return disp_field """