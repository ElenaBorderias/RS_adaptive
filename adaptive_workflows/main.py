
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
    try:
        patient = get_current("Patient")
        patient.Save()
    except:
        print("No patient loaded")

    #patient_list = ["ANON6","ANON12","ANON16","ANON18","ANON26","ANON29","ANON34","ANON37","ANON38","ANON43"]
    patient_list = ["ANON38"]
    model_list = ["0_NoAdapt","1_AutoRS_def_rois", "2_MimClin_rr_rois"]
    #model_list = ["2_MimClin_rr_rois"]

    for patient_name in patient_list:

        pat = Patient(patient_name)
        RS_Patient = pat.loadPatient()

        RS_Patient.Cases[0].SetCurrent()

        case = get_current("Case")
        patient = get_current("Patient")
        pct_name = "pCT"
        initial_plan = "ML_IMPT_plan"
        results_planning = evaluate_initial_planning(initial_plan)

        treatment_schedule_folder = "C:\\Elena\\results\\treatment_schedules"
        timing_folder = "C:\\Elena\\results\\timing"
        stats_folder = "C:\\Elena\\results\\dose_statistics"

        #export initial planning results
        results_planning_file = join(stats_folder, patient.Name + "_initial_planning.xlsx")
        results_planning.to_excel(results_planning_file, engine='openpyxl')

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

        #dataframe initialisations
        df_timing = pd.DataFrame(columns=["#Fraction", "Plan_image", "Plan_name", "t_plan_generation (min)", "t_plan_optimization (min)"])
        all_results = pd.DataFrame(columns=["Patient", "Plan_name", "ClinicalGoal", "Value"])
        all_patients_results = all_results

        for model in model_list:
            delete_all_dose_evaluations()
            model_paramters = read_model_param(model)

            for i in range(len(schedule)):

                n_fx = schedule.loc[i, '#Fraction']
                adapt_image_name = schedule.loc[i, 'CBCT_name']
                cbct_name = adapt_image_name[-7:]
                needs_adapt = schedule.loc[i, 'Needs_adaptation_0_1']
                
                if model.startswith("0"):
                    needs_adapt = 0
                    
                print(n_fx, adapt_image_name, needs_adapt)

                case.Examinations[adapt_image_name].ImportFraction = int(adapt_image_name[-2:])

                #adaption image generation
                if "Corrected " + cbct_name not in exam_names:
                    converter = CreateConvertedImage(pct_name, cbct_name, model_rois)
                    adapt_image_name = converter.create_corrected_cbct()
                else:
                    print("The adaptation image already exist: ", adapt_image_name)
                
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

                        df_timing = df_timing.append({'#Fraction': n_fx, 'Plan_image': adapt_image_name, 'Plan_name': auto_plan_name,
                                        't_plan_generation (min)': t_plan_generation/60, 't_plan_optimization (min)': t_plan_optimization/60}, ignore_index=True)

                        plan_names.append(auto_plan_name)
                        print(plan_names)

                    case.TreatmentPlans[auto_plan_name].BeamSets[0].ComputeDoseOnAdditionalSets(
                        OnlyOneDosePerImageSet=False, AllowGridExpansion=True, ExaminationNames=[adapt_image_name], FractionNumbers=[0], ComputeBeamDoses=True)
                
                elif needs_adapt == 0:
                    print("Adaptation is not needed for ", adapt_image_name,". I will recompute the initial plan")
                    
                    case.TreatmentPlans[initial_plan].BeamSets[0].ComputeDoseOnAdditionalSets(
                        OnlyOneDosePerImageSet=False, AllowGridExpansion=True, ExaminationNames=[adapt_image_name], FractionNumbers=[0], ComputeBeamDoses=True)
                    
                    #run DIR for dose deformation
                    auto_planning.run_DIR_pCT_adapt_image()

                # fraction on dose
                dose_on_examination = find_dose_on_examination(adapt_image_name)
                fx_dose = dose_on_examination.DoseEvaluations[0]
                print(fx_dose)
                print(dose_on_examination.DoseEvaluations[0])

                # map fraction dose
                try:
                    dir_reg_name = 'HybridDefReg'+adapt_image_name[-2:]+str(1)
                    case.MapDose(FractionNumber=0, SetTotalDoseEstimateReference=True, DoseDistribution=fx_dose,
                                StructureRegistration=case.StructureRegistrations[dir_reg_name], ReferenceDoseGrid=None)
                except:
                    print("There is no dose to evaluate in ", adapt_image_name)

            # accumulate all fraction doses on the planning ct
            doses_to_sum = []
            weights = []

            dose_on_examination_pct = find_dose_on_examination(pct_name)
            for dose_eval in dose_on_examination_pct.DoseEvaluations:
                doses_to_sum.append(dose_eval)
                weights.append(1)

            #create summed dose
            summed_dose_name = model_paramters['Alias'] + "Summed dose"
            case.CreateSummedDose(DoseName=model_paramters['Alias'] + "Summed dose", FractionNumber=0,
                                DoseDistributions=doses_to_sum,
                                Weights=weights)
            
            patient.Save()
            oa_strategy = model_paramters['OAStrategy']

            #evaluate summed dose
            evaluation = EvaluationSummedDose(dose_on_examination_pct,oa_strategy,summed_dose_name)
            results = evaluation.evaluate_dose_statistics()
            
            #write results
            results_file = join(stats_folder, patient.Name + "_" + oa_strategy + ".xlsx")
            results.to_excel(results_file, engine='openpyxl')

            all_results = all_results.append(results)
        
        # export results for all strategies and sum over fractions
        all_results_file = join(stats_folder, patient.Name + "_all_strategies" + ".xlsx")
        all_results.to_excel(all_results_file, engine='openpyxl')

        all_patients_results = all_patients_results.append(all_results)

        # export timing for all strategies and all fractions
        print('Tiiming data frame: ', df_timing)
        if len(df_timing) != 0:
            export_file = join(timing_folder, patient.Name + "_timing.xlsx")
            df_timing.to_excel(export_file, engine='openpyxl')

    #export results for all patients, all strategies and sum over fractions
    all_patient_results_file = join(stats_folder,"results_all_strategies_all_patients" + ".xlsx")
    all_patients_results.to_excel(all_patient_results_file, engine='openpyxl')

if __name__ == "__main__":
    main()
