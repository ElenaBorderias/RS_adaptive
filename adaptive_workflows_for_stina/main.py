
import imp
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan
from create_virtual_ct_from_cbct import CreateConvertedImage
from evaluation import EvaluationSummedDose, EvaluationPlanningDose
from Patients import Patient
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

def evaluate_initial_planning(plan_name):
    eval = EvaluationPlanningDose(plan_name)
    planning_results = eval.evaluate_dose_statistics()
    return planning_results

def main():

    model_list = ["2_MimClin_rr_rois"]

    case = get_current("Case")
    patient = get_current("Patient")
    pct_name = "pCT"
    initial_plan = "ML_IMPT_plan"

    plan_names = [plan.Name for plan in case.TreatmentPlans]

    for model in model_list:
        model_paramters = read_model_param(model)
            
        cbct_name = 'CBCT 04'
        adapt_image_name = 'Corrected CBCT 04'

        auto_plan_name = model_paramters['Alias'] + cbct_name
        #initialisation
        auto_planning = CreateIMPTPlan(adapt_image_name, auto_plan_name, 
                                                model_paramters['ModelName'], 
                                                model_paramters['ModelStrategy'],  
                                                model_paramters['ROI_mapping'], 
                                                model_paramters['DoseGrid'], 
                                                model_paramters['Needs_reference_dose'])
        needs_adapt = 1
        if needs_adapt == 1:
            print("Adaptation is needed for ", adapt_image_name)
            
            if auto_plan_name not in plan_names:
                #run planning
                auto_planning.create_run_and_approve_IMPT_plan()

if __name__ == "__main__":
    main()
