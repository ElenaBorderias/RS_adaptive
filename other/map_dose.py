
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


#create deformable registration
case.PatientModel.CreateHybridDeformableRegistrationGroup(RegistrationGroupName="Temp_reg",
                                                                ReferenceExaminationName=pct_name,
                                                                TargetExaminationNames=[reference_ct_name],
                                                                ControllingRoiNames=[], ControllingPoiNames=[], FocusRoiNames=[],
                                                                AlgorithmSettings={'NumberOfResolutionLevels': 3,
                                                                                  'InitialResolution': {'x': 0.5, 'y': 0.5, 'z': 0.5},
                                                                                  'FinalResolution': {'x': 0.25, 'y': 0.25, 'z': 0.25},
                                                                                  'InitialGaussianSmoothingSigma': 2,
                                                                                  'FinalGaussianSmoothingSigma': 0.333333333333333,
                                                                                  'InitialGridRegularizationWeight': 1500,
                                                                                  'FinalGridRegularizationWeight': 1000,
                                                                                  'ControllingRoiWeight': 0.5, 'ControllingPoiWeight': 0.1,
                                                                                  'MaxNumberOfIterationsPerResolutionLevel': 1000,
                                                                                  'ImageSimilarityMeasure': "CorrelationCoefficient",
                                                                                  'DeformationStrategy': "Default", 'ConvergenceTolerance': 1E-05})

#dir_reg = case.StructureRegistrations[case.StructureRegistrations.Count-1]

#find DIR
for reg in case.Registrations:
  for structure_reg in reg.StructureRegistrations:
    if structure_reg.Name  == "Temp_reg1":
      dir_reg = structure_reg

#set deformation field to 0
data = dir_reg.DeformationMatrix
disp_field = len(data)*[0]
disp_field = bytearray(disp_field)
dir_reg.SetDisplacementField(DisplacementField = disp_field)

#map dose to converted image
dose_to_map = reference_plan.TreatmentCourse.TotalDose
ref_dose_grid = case.TreatmentPlans[ml_plan_name].PlanOptimizations[0].OptimizationReferenceDose.InDoseGrid

case.MapDose(FractionNumber=0,SetTotalDoseEstimateReference=False,
    DoseDistribution=dose_to_map, StructureRegistration=dir_reg,ReferenceDoseGrid=ref_dose_grid)

"""
from_FOR = case.TreatmentPlans["ML_IMPT_plan"].PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference
to_FOR = case.TreatmentPlans["1_Mim_CBCT 02"].PlanOptimizations[0].TreatmentCourseSource.TotalDose.InDoseGrid.FrameOfReference

rig_transf_DF = case.GetTotalTransformForExaminations(FromExamination="Corrected CBCT 02",ToExamination="pCT")
regid_transf_FoR = case.GetTotalTransformForExaminations(FromExamination="Corrected CBCT 02",ToExamination="pCT")
#new_corner = case.TransformPointFromFoRToFoR(FromFrameOfReference=from_FOR,ToFrameOfReference=to_FOR,Point=corner)

case.CreateNewDeformableRegistration(ReferenceExaminationName="Corrected CBCT 02",TargetExaminationName="pCT",
                                      RegistrationName="Reg_for_transformation",RigidTransformDF=rig_transf_DF,
                                      RigidTransformFoR=regid_transf_FoR,FromFrameOfReference=from_FOR, ToFrameOfReference=to_FOR,
                                      GridCorner=corner, GridVoxelSize=vox_siz,NrOfVoxels=nr_vox,DisplacementField=displacement_field)
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