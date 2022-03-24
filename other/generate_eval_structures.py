# Script recorded 23 Mar 2022, 14:22:15

#   RayStation version: 12.0.110.63
#   Selected patient: ...

from connect import *

case = get_current("Case")
examination_list = ['Corrected CBCT 05', 'Corrected CBCT 34']

ctv_names = ["CTVnR_5425", "CTVnL_5425", "CTVp_7000", "CTV_5425", "CTV_7000"]

oar_names =["Mandible", "Esophagus", "SpinalCord", "Parotid_R", "Parotid_L", "Submandibular_L", "Submandibular_R", "Brainstem",
                            "Oral_Cavity", "PharConsSup", "PharConsMid", "PharConsInf"]
        
other_ctvs = ["CTVp_5425", "CTVnR_7000", "CTVnL_7000", "CTVn_7000"]

all_rois = case.PatientModel.StructureSets["pCT"].RoiGeometries
roi_names = [x.OfRoi.Name for x in all_rois]

for extra_ctv in other_ctvs:
    if extra_ctv in roi_names:
        oar_names.append(extra_ctv)


ref_rois = ctv_names + oar_names
for exam in examination_list:
  for roi in ref_rois:
    ref_roi = case.PatientModel.StructureSets[exam].RoiGeometries[roi]
    eval_roi_name = 'eval_' + roi
    color = ref_roi.OfRoi.Color
    type =  ref_roi.OfRoi.Type
    try:
      retval_0 = case.PatientModel.CreateRoi(Name= eval_roi_name, Color= color, Type= type, TissueName=None, RbeCellTypeName=None, RoiMaterial= None)
      retval_0.CreateMarginGeometry(Examination=case.Examinations[exam], SourceRoiName=roi, MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
    except:
      print('the ROI has been generated already')
      case.PatientModel.RegionsOfInterest[eval_roi_name].CreateMarginGeometry(Examination=case.Examinations[exam], SourceRoiName=roi, MarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

