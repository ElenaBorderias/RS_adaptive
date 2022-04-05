# Script recorded 28 Feb 2022, 13:55:32

#   RayStation version: 12.0.110.55
#   Selected patient: ...

from connect import *

case = get_current("Case")
patient = get_current("Patient")

for doe in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
	n_evals = len(doe.DoseEvaluations)
	if n_evals != 0:
		for i in range(len(doe.DoseEvaluations)-1,-1,-1):
			dose_eval = doe.DoseEvaluations[i]
			dose_eval.DeleteEvaluationDose()

patient.Save()