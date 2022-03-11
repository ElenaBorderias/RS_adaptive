
from connect import get_current


def find_dose_on_examination(examination_name):
    case = get_current("Case")
    for i,doe in enumerate(case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations):
        if doe.OnExamination.Name == examination_name:
            dose_on_examination = doe
            index_doe = i
    return dose_on_examination, index_doe

def delete_all_dose_evaluations():
    case = get_current("Case")
    for doe in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
        if len(doe.DoseEvaluations) != 0:
            for dose_eval in doe.DoseEvaluations:
                dose_eval.DeleteEvaluationDose()

def main():

    case = get_current("Case")
    patient = get_current("Patient")
    pct_name = "pCT"
    initial_plan = "ML_IMPT_plan"
    doe,index_doe = find_dose_on_examination("Corrected CBCT 01")
    print(doe)
    fe = case.TreatmentDelivery.FractionEvaluations[0]
    dose = fe.DoseOnExaminations[index_doe].DoseEvaluations[0]
    print(dose)

if __name__ == "__main__":
    main()
