# Script recorded 28 Feb 2022, 13:55:32

#   RayStation version: 12.0.110.55
#   Selected patient: ...

from connect import *

case = get_current("Case")
patient = get_current("Patient")

corrected_cbct_list = []
for exam in case.Examinations:
	if exam.Name.startswith("CBCT"):
		corrected_cbct_list.append(exam.Name)

for corr_cbct in corrected_cbct_list:

	case.DeleteExamination(ExaminationName=corr_cbct)

patient.Save()