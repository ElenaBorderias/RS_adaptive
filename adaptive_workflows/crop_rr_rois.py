# Script recorded 26 Apr 2022, 18:36:46

#   RayStation version: 12.0.110.63
#   Selected patient: ...

from connect import *
import json


def read_patient_ct_list(patient_name):
    _f = open('patients_parameters.json')
    properties = json.load(_f)
    _f.close()
    return properties[patient_name]

def main():
  patient = get_current('Patient')
  case = get_current("Case")

  rr_rois = ['rr_CTV_7000','rr_CTV_5425']
  pat_ct_info = read_patient_ct_list(patient.Name)
  ct_list = [pat_ct_info['CT1'], pat_ct_info['CT2']]
  
  for ct in ct_list:
    examination = case.Examinations[ct]

    for rr_roi in rr_rois:
        case.PatientModel.RegionsOfInterest[rr_roi].CreateAlgebraGeometry(Examination=examination, Algorithm="Auto", 
        ExpressionA={'Operation': "Union", 'SourceRoiNames': [rr_roi], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, 
        ExpressionB={'Operation': "Union", 'SourceRoiNames': ["BODY"], 'MarginSettings': {'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0}}, 
        ResultOperation="Intersection", ResultMarginSettings={'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0})


if __name__ == "__main__":
    main()
