
import imp
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan

import pandas as pd
from os.path import join
import json

def read_model_param(model_name):
    _f = open('model_parameters.json')
    properties = json.load(_f)
    _f.close()
    return properties[model_name]


def main():
    
    patient = get_current("Patient")
    model_list = ["2_MimClin_rr_rois"]

    case = get_current("Case")

    pct_name = "pCT"
    initial_plan = "ML_IMPT_plan"

    plan_names = [plan.Name for plan in case.TreatmentPlans]

    for model in model_list:
        model_paramters = read_model_param(model)

        n_fx = 4
        adapt_image_name = 'Corrected CBCT 04'
        cbct_name = 'CBCT 04'
        needs_adapt = 1

        print(n_fx, adapt_image_name, needs_adapt)

        case.Examinations[adapt_image_name].ImportFraction = int(adapt_image_name[-2:])
        
        auto_plan_name = model_paramters['Alias'] + cbct_name
        
        #initialisation
        auto_planning = CreateIMPTPlan(adapt_image_name, auto_plan_name, 
                                                model_paramters['ModelName'], 
                                                model_paramters['ModelStrategy'],  
                                                model_paramters['ROI_mapping'], 
                                                model_paramters['DoseGrid'], 
                                                model_paramters['Needs_reference_dose'])
        
        print('Model parameters: ', model_paramters)
        if needs_adapt == 1:
            print("Adaptation is needed for ", adapt_image_name)
            
            if auto_plan_name not in plan_names:
                #run planning
                t_plan_generation, t_plan_optimization = auto_planning.create_run_and_approve_IMPT_plan()

        print(t_plan_generation, t_plan_optimization)
            
if __name__ == "__main__":
    main()
