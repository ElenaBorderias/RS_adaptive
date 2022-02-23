
from connect import get_current
from create_IMPT_plan import CreateIMPTPlan
from create_virtual_ct_from_cbct import CreateConvertedImage
from evaluation import NeedsAdaptation, EvaluateClinicalPlan
import pandas as pd

def main():

    pct_name = "pCT"
    reference_plan_name = "ML_IMPT_plan"

    patient = get_current("Patient")
    case = get_current("Case")
    cbct_names_list = []

    exam_names = [ex.Name for ex in case.Examinations]
    for exam in exam_names:
        if exam.startswith("CBCT"):
            cbct_names_list.append(exam)
    
    run_1_auto_planning = False
    run_2_mimicking_plan = False

    oars_model = [r"Brainstem", r"SpinalCord",
                  r"Parotid_R", r"Parotid_L", r"Submandibular_L", r"Submandibular_R",
                  r"Oral_Cavity", r"PharConsSup", r"PharConsMid", r"PharConsInf",
                  r"Esophagus", r"BODY"]

    targets_model = [r"CTV_5425", r"CTV_7000", r"CTV_all", r"CTVp_7000", r"CTV_7000+10mm", r"CTV54.25-CTV70+10mm"]

    model_rois = targets_model + oars_model

    df = pd.DataFrame(columns = ["#Fraction","CBCT_name","Needs_adaptation", "D98_CTV_5425","D98_CTV_7000"])
    cbct_names_list = ['CBCT 01','CBCT 02','CBCT 03']

    for i,cbct_name in enumerate(cbct_names_list):

        case.Examinations[cbct_name].ImportFraction = int(cbct_name[-2:])
        converter = CreateConvertedImage(pct_name, cbct_name, model_rois)

        if "Corrected " + cbct_name not in exam_names:
            adapt_image_name = converter.create_corrected_cbct()
        else:
            adapt_image_name = "Corrected " + cbct_name
        
        #init_eval = EvaluateClinicalPlan(adapt_image_name, reference_plan_name)
        #init_eval.map_rois_deformably()
        
        init_adapt = NeedsAdaptation(adapt_image_name, reference_plan_name)
        adapt, ctv_low_coverage, ctv_high_coverage = init_adapt.check_adaptation_needed()

        df = df.append({'#Fraction' : int(cbct_name[-2:]), 'CBCT_name' : adapt_image_name, 'Needs_adaptation' : adapt, 'D98_CTV_5425':ctv_low_coverage, 'D98_CTV_7000': ctv_high_coverage},ignore_index = True)
        print(df)

    export_file = "C:\\Elena\\results\\" + patient.Name + "_ttmt_schedule.xlsx"
    df.to_excel(export_file, engine='openpyxl')
    

if __name__ == "__main__":
    main()
