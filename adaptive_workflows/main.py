
import imp
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan
from create_virtual_ct_from_cbct import CreateConvertedImage
from evaluation import NeedsAdaptation
import pandas as pd
from os.path import join


def main():

    case = get_current("Case")
    patient = get_current("Patient")
    pct_name = "pCT"
    initial_plan = "ML_IMPT_plan"

    treatment_schedule_folder = "C:\\Elena\\results\\treatment_schedules"

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
    schedule = schedule.loc[:, ['#Fraction', 'CBCT_name', 'Needs_adaptation']]
    
    for i in range(len(schedule)):
        if i < 5:
            n_fx = schedule.loc[i, '#Fraction']
            adapt_image_name = schedule.loc[i, 'CBCT_name']
            cbct_name = adapt_image_name[-7:]
            needs_adapt = schedule.loc[i, 'Needs_adaptation']

            print(n_fx,adapt_image_name,needs_adapt)

            case.Examinations[adapt_image_name].ImportFraction = int(adapt_image_name[-2:])
            
            if "Corrected " + cbct_name not in exam_names:
                converter = CreateConvertedImage(pct_name, cbct_name, model_rois)
                adapt_image_name = converter.create_corrected_cbct()
            else:
                print("The adaptation image already exist: ", adapt_image_name)
            
            if needs_adapt:
            # Prediction + Mimicking
                auto_plan_name = "1_Auto_" + cbct_name
                if auto_plan_name not in plan_names:
                    auto_planning = CreateIMPTPlan(adapt_image_name, auto_plan_name, "RSL_IMPT_conv_img", "IMPT Demo", "DIR","Default", False)
                    auto_planning.create_run_and_approve_IMPT_plan()
                    
                case.TreatmentPlans[auto_plan_name].BeamSets[0].ComputeDoseOnAdditionalSets(OnlyOneDosePerImageSet=False, AllowGridExpansion=True, ExaminationNames=[adapt_image_name], FractionNumbers=[0], ComputeBeamDoses=True)

            else: 
                case.TreatmentPlans[initial_plan].BeamSets[0].ComputeDoseOnAdditionalSets(OnlyOneDosePerImageSet=False, AllowGridExpansion=True, ExaminationNames=[adapt_image_name], FractionNumbers=[0], ComputeBeamDoses=True)


            
            """
            if run_2_mimicking_plan:
            # Clinical dose + Mimicking
                mimick_plan_name = "2_Mim_" + cbct_name
                mimicking_from_clinical = CreateIMPTPlan(adapt_image_name, mimick_plan_name, "Only_mimicking_conv_img", "IMPT Demo", "RigidReg","Copy_from_plan", True)
                mimicking_from_clinical.create_run_and_approve_IMPT_plan()
            """
        

if __name__ == "__main__":
    main()
