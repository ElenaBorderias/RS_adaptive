
import imp
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan
from create_virtual_ct_from_cbct import CreateConvertedImage
from evaluation import EvaluationSummedDose
import pandas as pd
from os.path import join
import json


def find_dose_on_examination(examination_name):
    case = get_current("Case")
    for doe in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
        if doe.OnExamination.Name == examination_name:
            dose_on_examination = doe
    return dose_on_examination


def delete_all_dose_evaluations():
    case = get_current("Case")
    for doe in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
        n_evals = len(doe.DoseEvaluations)
        if n_evals != 0:
            for i in range(len(doe.DoseEvaluations)-1,-1,-1):
                dose_eval = doe.DoseEvaluations[i]
                dose_eval.DeleteEvaluationDose()


def read_model_param(model_name):
    _f = open('model_parameters.json')
    properties = json.load(_f)
    _f.close()
    return properties[model_name]

def main():

    case = get_current("Case")
    patient = get_current("Patient")
    pct_name = "pCT"
    initial_plan = "ML_IMPT_plan"

    treatment_schedule_folder = "C:\\Elena\\results\\treatment_schedules"
    timing_folder = "C:\\Elena\\results\\timing"

    plan_names = [plan.Name for plan in case.TreatmentPlans]
    exam_names = [exam.Name for exam in case.Examinations]

    oars_model = [r"Brainstem", r"SpinalCord",
                  r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
                  r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
                  r"Esophagus", r"BODY"]

    targets_model = [r"CTV_5425", r"CTV_7000", r"CTV_all",
                     r"CTVp_7000", r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

    model_rois = targets_model + oars_model

    file = patient.Name + "_ttmt_schedule.xlsx"
    schedule = pd.read_excel(join(treatment_schedule_folder, file))
    schedule = schedule.loc[:, ['#Fraction', 'CBCT_name',
                                'Needs_adaptation', 'Needs_adaptation_0_1']]

    df_timing = pd.DataFrame(columns=[
                             "#Fraction", "Plan_image", "Plan_name", "t_plan_generation", "t_plan_optimization"])

    #model_list = ["1_AutoRS_def_rois", "2_MimClin_rr_rois"]
    model_list = ["1_AutoRS_def_rois"]
    
    for model in model_list:
        model_paramters = read_model_param(model)
        dose_on_examination_pct = find_dose_on_examination(pct_name)

        #create and evaluate summed dose
        summed_dose_name = model_paramters['Alias'] + "Summed dose"
        oa_strategy = model_paramters['OAStrategy']
        evaluation = EvaluationSummedDose(dose_on_examination_pct,oa_strategy,summed_dose_name)
        results = evaluation.evaluate_dose_statistics()
        results_file = join(timing_folder, patient.Name + "_" + oa_strategy + ".xlsx")
        results.to_excel(results_file, engine='openpyxl')


    # export timing for all fractions
    export_file = join(timing_folder, patient.Name + "_timing.xlsx")
    df_timing.to_excel(export_file, engine='openpyxl')


if __name__ == "__main__":
    main()
