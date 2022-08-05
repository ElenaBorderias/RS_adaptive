
import imp
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan
from create_virtual_ct_from_cbct import CreateConvertedImage
from evaluation import EvaluationPlanningDose, EvaluationPlanningDose_real_contours
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

def read_model_param(model_name):
    _f = open('model_parameters.json')
    properties = json.load(_f)
    _f.close()
    return properties[model_name]

def read_patient_ct_list(patient_name):
    path =  'C:\\Elena\\results_NTCP\\treatment_schedules'
    patient_path = join(path,patient_name+'_ttmt_schedule.xlsx')
    patient_info = pd.read_excel(patient_path)
    repeated_images_list = patient_info['CBCT_name']
    adaptation_schedule =  patient_info['Needs_adaptation_0_1']
    return repeated_images_list, adaptation_schedule

def delete_all_dose_evaluations():
    case = get_current("Case")
    for doe in case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
        n_evals = len(doe.DoseEvaluations)
        if n_evals != 0:
            for i in range(len(doe.DoseEvaluations)-1,-1,-1):
                dose_eval = doe.DoseEvaluations[i]
                dose_eval.DeleteEvaluationDose()


def main():
    try:
        patient = get_current("Patient")
        patient.Save()
    except:
        print("No patient loaded")

    #patient_list = ["ANON12","ANON16","ANON18","ANON26","ANON29","ANON34","ANON37","ANON38","ANON43","ANON6"]
    #patient_list = ["ANON37","ANON26","ANON18"]
    patient_list = ["ANON34","ANON37","ANON38","ANON43","ANON6"]
    model_list = ["0_NoAdapt","1_AutoRS_def_rois", "2_MimClin_rr_rois","3_MimDef_def_rois"]
    
    for patient_name in patient_list:

        pat = Patient(patient_name)
        RS_Patient = pat.loadPatient()

        RS_Patient.Cases[0].SetCurrent()

        case = get_current("Case")
        patient = get_current("Patient")

        plan_names = [plan.Name for plan in case.TreatmentPlans]

        stats_folder = "C:\\Elena\\results_all_fractions\\dose_statistics"

        """
        oars_model = [r"Brainstem", r"SpinalCord",
                    r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
                    r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
                    r"Esophagus", r"BODY"]

        targets_model = [r"CTV_5425", r"CTV_7000", r"CTV_all",
                        r"CTVp_7000", r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

        model_rois = targets_model + oars_model
        """

        #dataframe initialisations
        df_timing = pd.DataFrame(columns=["#Fraction", "Plan_image", "Plan_name", "t_plan_generation (min)", "t_plan_optimization (min)"])
        all_results = pd.DataFrame(columns=["Patient", "Strategy","Adapt_image","Plan_name", "ClinicalGoal", "Value"])
        all_patients_results = all_results

        ct_list, adapt_schedule = read_patient_ct_list(patient.Name)

        for model in model_list:
            model_paramters = read_model_param(model)
            print(' EVALUATION ', model)

            all_ct_results = pd.DataFrame(columns=["Patient", "Strategy","Adapt_image","Plan_name", "ClinicalGoal", "Value","Needs_adapt","#Fraction"])

            for i,adapt_image_name in enumerate(ct_list):
                delete_all_dose_evaluations()
                cbct_name = adapt_image_name[-7:]
                print('Adaptation image: ', adapt_image_name)
                print('CBCT: ', cbct_name)
                bool_adapt = adapt_schedule[i]

                auto_plan_name = model_paramters['Alias'] + cbct_name
                
                if model.startswith('0'):
                    print('Running evaluation of ', model)
                    case.TreatmentPlans['ML_IMPT_plan'].BeamSets[0].ComputeDoseOnAdditionalSets(OnlyOneDosePerImageSet=False, AllowGridExpansion=True, ExaminationNames=[adapt_image_name], FractionNumbers=[0], ComputeBeamDoses=True)
                    oa_strategy = model_paramters['OAStrategy']
                    evaluation = EvaluationPlanningDose_real_contours(auto_plan_name,adapt_image_name,i+1,0)
                    results = evaluation.evaluate_dose_statistics()
                    results['Needs_adapt'] = [bool_adapt]*len(results['Patient'])
                    results['#Fraction'] = [i+1]*len(results['Patient'])

                else:
                    #initialisation
                    auto_planning = CreateIMPTPlan(adapt_image_name, auto_plan_name, 
                                                            model_paramters['ModelName'], 
                                                            model_paramters['ModelStrategy'],  
                                                            model_paramters['ROI_mapping'], 
                                                            model_paramters['DoseGrid'], 
                                                            model_paramters['Needs_reference_dose'])
                    if bool_adapt == 1:
                        if auto_plan_name not in plan_names:
                            print('Your plan didnt existed, I will create ', auto_plan_name)
                            #run planning
                            t_plan_generation, t_plan_optimization = auto_planning.create_run_and_approve_IMPT_plan()

                            df_timing = df_timing.append({'#Fraction': 'eval', 'Plan_image': adapt_image_name, 'Plan_name': auto_plan_name,
                                                't_plan_generation (min)': t_plan_generation/60, 't_plan_optimization (min)': t_plan_optimization/60}, ignore_index=True)

                            oa_strategy = model_paramters['OAStrategy']
                        else:
                            print('The plan you want to evaluate already exists : ', auto_plan_name)
                            oa_strategy = model_paramters['OAStrategy']
                            #case.TreatmentPlans[auto_plan_name].TreatmentCourse.TotalDose.UpdateDoseGridStructures()

                        print('Running evaluation of ', model)
                        evaluation = EvaluationPlanningDose(auto_plan_name)
                        results = evaluation.evaluate_dose_statistics()
                        results['Needs_adapt'] = [bool_adapt]*len(results['Patient'])
                        results['#Fraction'] = [i+1]*len(results['Patient'])
                        results['Strategy'] = [ model_paramters['Alias']]*len(results['Patient'])
                        results["Adapt_image"] =  [adapt_image_name]*len(results['Patient'])

                    
                    if bool_adapt == 0:
                        na_results_df = pd.read_excel(join(stats_folder,patient.Name+'_0_NoAdapt.xlsx'))
                        na_results = na_results_df[na_results_df['#Fraction'] == i+1]
                        results = na_results
                
                all_ct_results = all_ct_results.append(results)

            #write results
            results_file = join(stats_folder, patient.Name + "_" + oa_strategy + ".xlsx")
            all_ct_results.to_excel(results_file, engine='openpyxl')

            all_results = all_results.append(all_ct_results)
    
        # export results for all strategies and sum over fractions
        all_results_file = join(stats_folder, patient.Name + "_all_strategies" + ".xlsx")
        all_results.to_excel(all_results_file, engine='openpyxl')

        all_patients_results = all_patients_results.append(all_results)

    #export results for all patients, all strategies and sum over fractions
    all_patient_results_file = join(stats_folder,"results_all_strategies_all_patients" + ".xlsx")
    all_patients_results.to_excel(all_patient_results_file, engine='openpyxl')

if __name__ == "__main__":
    main()
