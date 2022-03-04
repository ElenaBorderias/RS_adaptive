# Script recorded 04 Mar 2022, 09:33:10

#   RayStation version: 12.0.110.55
#   Selected patient: ...

from connect import *

case = get_current("Case")

examination_list = ["pCT"]

for exam in examination_list:
    examination = case.Examinations[exam]
    examination.RunOarSegmentation(ModelName="RSL Head and Neck CT",
                                   ExaminationsAndRegistrations={
                                       exam: None},
                                   RoisToInclude=["DL_Brainstem", "DL_Esophagus_S", "DL_Oral_Cavity",
                                                  "DL_Parotid_L", "DL_Parotid_R", "DL_SpinalCord", "DL_Submandibular_L", "DL_Submandibular_R"])
